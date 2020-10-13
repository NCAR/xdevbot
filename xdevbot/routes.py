import asyncio
import json
import logging

from aiohttp import web

from xdevbot import github, projects, queries, utils

logger = logging.getLogger('xdevbot')

CONFIG_URL = 'https://raw.githubusercontent.com/NCAR/xdev/xdevbot/xdevbot.yaml'


async def github_handler(request: web.Request) -> web.Response:
    event = await github.Event(request)
    logger.info(f'Event Received: {event.type}/{event.action}')
    handler = github.router(event)
    return await handler(event)


@github.route('issues', 'opened')
@github.route('pull_request', 'opened')
async def opened(event: github.EventType):
    ref = event.payload[event.key]['html_url']
    logger.debug(f'Triggered {event.key}/{event.action} event handler from ref {ref}')

    repo = event.payload['repository']['full_name']

    cfg_data = await utils.read_remote_yaml(CONFIG_URL)
    df = projects.build_config_frame(cfg_data)
    project_urls = df[df['repo'] == repo]['project_url'].to_list()
    if len(project_urls) == 0:
        logger.debug(f'No projects associated with repo {repo}')
        return web.Response()

    token = event.app['token']
    column_data = await github.graphql_query(queries.GET_COLUMNS, token=token)
    columns_df = projects.build_columns_frame(column_data)
    column_name = 'In Progress' if event.key == 'pull_request' else 'New'

    async with github.ProjectClientSession(token=token) as session:
        for project_url in project_urls:
            logger.info(f'Creating new card on project {project_url}')
            df = columns_df[columns_df['project_url'] == project_url]
            column_id = int(df[df['column_name'] == column_name]['column_id'])
            response = await session.create_project_card(note=ref, column_id=column_id)
            if response.status != 201:
                logger.warning(f'Failed to create new card! [{response.status}]')
                body = json.dumps(await response.json(), indent=4)
                logger.debug(f'HTTP Response Body:\n{body}')
            await asyncio.sleep(0.1)

    await utils.log_rate_limits(token=token)

    return web.Response()


@github.route('issues', 'closed')
@github.route('issues', 'reopened')
@github.route('pull_request', 'closed')
@github.route('pull_request', 'reopened')
async def closed(event: github.EventType):
    ref = event.payload[event.key]['html_url']
    logger.debug(f'Triggered {event.key}/{event.action} event handler from ref {ref}')

    token = event.app['token']
    card_data = await github.graphql_query(queries.GET_ALL_CARDS, token=token)
    cards_df = projects.build_cards_frame(card_data)

    matching_cards = cards_df[cards_df['ref'] == ref]
    if len(matching_cards) == 0:
        logger.debug(f'No cards found matching ref {ref}')
        return web.Response()

    df_column = 'in_progress_column_id' if event.action == 'reopened' else 'done_column_id'
    async with github.ProjectClientSession(token=token) as session:
        for _, card in matching_cards.iterrows():
            card_id = int(card['card_id'])
            column_id = int(card[df_column])
            logger.info(f'Moving card {card_id} to column {column_id}')
            response = await session.move_project_card(card_id=card_id, column_id=column_id)
            if response.status != 201:
                logger.warning(f'Failed to move card [{response.status}]')
            await asyncio.sleep(0.1)

    await utils.log_rate_limits(token=token)

    return web.Response()


@github.route('project_card', 'moved')
async def moved(event: github.EventType):
    mover = event.payload['sender']['login']
    if mover == 'xdev-bot':
        return web.Response()

    moved_card_id = event.payload[event.key]['id']

    note = event.payload[event.key]['note']
    refs = utils.refs_from_note(note)
    if len(refs) != 1:
        logger.debug(f'No cards found matching note: {note}')
        return web.Response()
    ref = refs[0]
    logger.debug(f'Triggered {event.key}/{event.action} event handler from note "{note}"')

    token = event.app['token']
    all_card_data = await github.graphql_query(queries.GET_ALL_CARDS, token=token)
    cards_df = projects.build_cards_frame(all_card_data)

    moved_card = cards_df[cards_df['card_id'] == moved_card_id]
    if len(moved_card) != 1:
        logger.debug(f'Could not find moved card {moved_card_id}')
        return web.Response()
    moved_column_name = moved_card['column_name'].to_list()[0]
    df_column = f'{moved_column_name.lower().replace(" ", "_")}_column_id'

    matching_cards = cards_df[cards_df['ref'] == ref]
    other_cards = matching_cards[matching_cards['card_id'] != moved_card_id]
    if len(other_cards) == 0:
        logger.debug(f'No other cards found matching ref {ref}')
        return web.Response()

    async with github.ProjectClientSession(token=token) as session:
        for _, card in other_cards.iterrows():
            card_id = int(card['card_id'])
            column_id = int(card[df_column])
            logger.info(f'Moving card {card_id} to column {column_id}')
            response = await session.move_project_card(card_id=card_id, column_id=column_id)
            if response.status != 201:
                logger.warning(f'Failed to move card [{response.status}]')
            await asyncio.sleep(0.1)

    await utils.log_rate_limits(token=token)

    return web.Response()


@github.route('project_card', 'deleted')
async def deleted(event: github.EventType):
    deleter = event.payload['sender']['login']
    if deleter == 'xdev-bot':
        return web.Response()

    deleted_card_id = event.payload[event.key]['id']

    note = event.payload[event.key]['note']
    refs = utils.refs_from_note(note)
    if len(refs) != 1:
        logger.debug(f'No cards found matching note: {note}')
        return web.Response()
    ref = refs[0]
    logger.debug(f'Triggered {event.key}/{event.action} event handler from note "{note}"')

    token = event.app['token']
    all_card_data = await github.graphql_query(queries.GET_ALL_CARDS, token=token)
    cards_df = projects.build_cards_frame(all_card_data)
    matching_cards = cards_df[cards_df['ref'] == ref]
    other_cards = matching_cards[matching_cards['card_id'] != deleted_card_id]
    if len(other_cards) == 0:
        logger.debug(f'No other cards found matching ref {ref}')
        return web.Response()

    async with github.ProjectClientSession(token=token) as session:
        for _, card in other_cards.iterrows():
            card_id = int(card['card_id'])
            logger.info(f'Deleting card {card_id}')
            response = await session.delete_project_card(card_id=card_id)
            if response.status != 204:
                logger.warning(f'Failed to delete card [{response.status}]')
            await asyncio.sleep(0.1)

    await utils.log_rate_limits(token=token)

    return web.Response()
