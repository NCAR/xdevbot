import logging

from aiohttp import web

from xdevbot import github, projects, queries, utils

logger = logging.getLogger('gunicorn.error')

CONFIG_URL = 'https://raw.githubusercontent.com/NCAR/xdev/xdevbot/xdevbot.yaml'


async def github_handler(request: web.Request) -> web.Response:
    event = await github.Event(request)
    logger.debug(f'Event Received: {event.type}/{event.action}')
    handler = github.router(event)
    return await handler(event)


@github.route('issues', 'opened')
@github.route('pull_request', 'opened')
async def opened(event: github.EventType):
    ref = event.payload[event.key]['html_url']
    content_id = event.payload[event.key]['id']
    content_type = 'Issue' if event.type == 'issues' else 'PullRequest'
    logger.debug(f'Received {event.key} {event.action} event: {ref}')

    repo = event.payload['repository']['full_name']

    cfg_data = await utils.read_remote_yaml(CONFIG_URL)
    df = projects.build_config_frame(cfg_data)
    project_urls = df[df['repo'] == repo]['project_url'].to_list()
    if len(project_urls) == 0:
        logger.debug(f'No projects associated with repo: {repo}')
        return web.Response()

    token = event.app['token']
    col_data = await github.graphql_query(queries.GET_COLUMNS, token=token)
    columns = projects.build_columns_frame(col_data)
    column_name = 'In Progress' if event.key == 'pull_request' else 'New'

    async with github.ProjectClientSession(token=token) as session:
        for project_url in project_urls:
            logger.debug(f'Creating new card on project: {project_url}')
            df = columns[columns['project_url'] == project_url]
            column_id = int(df[df['column_name'] == column_name]['column_id'])
            await session.create_project_card(
                content_id=content_id, content_type=content_type, column_id=column_id
            )

    return web.Response()


@github.route('issues', 'closed')
@github.route('issues', 'reopened')
@github.route('pull_request', 'closed')
@github.route('pull_request', 'reopened')
async def closed(event: github.EventType):
    ref = event.payload[event.key]['html_url']
    content_id = event.payload[event.key]['id']
    logger.debug(f'Received {event.key} {event.action} event: {ref}')

    token = event.app['token']
    card_data = await github.graphql_query(queries.GET_ALL_CARDS, token=token)
    df = projects.build_cards_frame(card_data)

    by_ref = df['ref'] == ref
    by_id = df['content_id'] == content_id
    cards = df[by_ref | by_id]
    if len(cards) == 0:
        logger.debug(f'No cards found matching ref: {ref}')
        return web.Response()

    df_column = 'inprog_column_id' if event.action == 'reopened' else 'done_column_id'
    async with github.ProjectClientSession(token=token) as session:
        for _, card in cards.iterrows():
            card_id = int(card['card_id'])
            column_id = int(card[df_column])
            logger.debug(f'Moving card {card_id} to column {column_id}')
            await session.move_project_card(card_id=card_id, column_id=column_id)

    return web.Response()
