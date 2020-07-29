import xdevbot.github as github


@github.route('issues', 'created')
async def issue_created(event: github.EventType):
    username = event.app['config']['github_username']
    token = event.app['config']['github_token']
    async with github.ProjectClientSession(username=username, token=token) as session:
        note = event.payload['issue']['html_url']
        column_id = 1234
        return await session.create_project_card(note=note, column_id=column_id)
