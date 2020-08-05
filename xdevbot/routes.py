from aiohttp import web

from xdevbot import github, projects, queries, utils

CONFIG_URL = 'https://raw.githubusercontent.com/NCAR/xdev/master/xdevbot.yaml'


async def handler(request: web.Request) -> web.Response:
    event = await github.Event(request)
    print(f'Event Received: {event.kind}/{event.action}')
    handler = github.router(event)
    return await handler(event)


@github.route('issues', 'opened')
@github.route('pull_request', 'opened')
async def opened(event: github.EventType):
    ref = event.payload[event.element]['html_url']
    repo = event.payload['repository']['full_name']
    print(f'Received {event.element} {event.action} event: {ref}')

    cfg_data = await utils.read_remote_yaml(CONFIG_URL)
    df = projects.build_config_frame(cfg_data)
    project_urls = df[df['repo'] == repo]['project_url'].to_list()
    if len(project_urls) == 0:
        print(f'No projects associated with repo: {repo}')
        return web.Response()

    token = event.app['token']
    col_data = await github.graphql_query(queries.GET_COLUMNS, token=token)
    columns = projects.build_columns_map(col_data)
    column_name = 'In Progress' if event.element == 'pull_request' else 'New'

    async with github.ProjectClientSession(token=token) as session:
        for project_url in project_urls:
            print(f'Creating new card on project: {project_url}')
            column_id = columns[project_url][column_name]
            await session.create_project_card(note=ref, column_id=column_id)

    return web.Response()


@github.route('issues', 'closed')
@github.route('issues', 'reopened')
@github.route('pull_request', 'closed')
@github.route('pull_request', 'reopened')
async def closed(event: github.EventType):
    ref = event.payload[event.element]['html_url']
    print(f'Received {event.element} {event.action} event: {ref}')

    token = event.app['token']
    card_data = await github.graphql_query(queries.GET_ALL_CARDS, token=token)
    df = projects.build_cards_frame(card_data)
    cards = df[df['ref'] == ref]
    if len(cards) == 0:
        print(f'No cards found matching ref: {ref}')
        return web.Response()

    column_name = 'inprog_column_id' if event.action == 'reopened' else 'done_column_id'
    async with github.ProjectClientSession(token=token) as session:
        for _, card in cards.iterrows():
            card_id = card['card_id']
            column_id = card[column_name]
            print(f'Moving card {card_id} to column {column_id}')
            await session.move_project_card(card_id=card_id, column_id=column_id)

    return web.Response()
