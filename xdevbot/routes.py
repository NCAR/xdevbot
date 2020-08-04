from aiohttp import web

from xdevbot import github, projects, utils


@github.route('issues', 'opened')
async def issue_opened(event: github.EventType):
    token = event.app['token']

    ref = event.payload['issue']['html_url']
    repo_url = event.payload['issue']['repository_url']
    repo = utils.repo_fullname_from_url(repo_url)

    cfg_df = await projects.get_config_frame()
    project_urls = cfg_df[cfg_df['repo'] == repo]['project_url'].to_list()
    if len(project_urls) == 0:
        return web.Response()

    all_df = await projects.get_cards_frame(token=token)
    crd_df = all_df[all_df['ref'] == ref]
    if len(crd_df) == 0:
        return web.Response()

    async with github.ProjectClientSession(token=token) as session:
        for project_url in project_urls:
            cards = crd_df[crd_df['project_url'] == project_url]
            for _, card in cards.iterrows():
                column_id = card['new_column_id']
                await session.create_project_card(note=ref, column_id=column_id)

    return web.Response()
