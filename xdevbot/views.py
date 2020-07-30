from xdevbot import github, utils


@github.route('issues', 'opened')
async def issue_opened(event: github.EventType):
    username = event.app['github_username']
    token = event.app['github_token']

    note = event.payload['issue']['html_url']
    repo_url = event.payload['issue']['repository_url']
    repo = utils.repo_fullname_from_url(repo_url)

    df = event.app['config']
    project_urls = df[df['repo'] == repo]['project_url'].to_list()

    async with github.ProjectClientSession(username=username, token=token) as session:
        for project_url in project_urls:
            column_id = event.app['columns'][project_url]['New']
            return await session.create_project_card(note=note, column_id=column_id)


# @github.route('issues', 'closed')
# async def issue_closed(event: github.EventType):
#     username = event.app['github_username']
#     token = event.app['github_token']

#     note = event.payload['issue']['html_url']

#     df = event.app['projects']
#     cards = df[df['note'] == note]
#     repo_url = event.payload['issue']['repository_url']
#     repo = utils.repo_fullname_from_url(repo_url)

#     df = event.app['config']
#     project_urls = df[df['repo'] == repo]['project_url'].to_list()

#     async with github.ProjectClientSession(username=username, token=token) as session:
#         for project_url in project_urls:

#             card_id = 234
#         # For each project board:
#         #     Find card_id for card with matching note
#         #     Find "Done" column_id for project board
#         #     return await session.move_project_card(card_id=card_id, column_id=column_id)
