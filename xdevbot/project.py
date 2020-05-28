import asyncio
import json
import logging
import os
from datetime import datetime

import aiohttp

logging.basicConfig(level=logging.INFO)

XDEVBOT_MAIN_ENDPOINT = 'http://xdevbot.herokuapp.com/gh/main'
XDEVBOT_WATCH_ENDPOINT = 'http://xdevbot.herokuapp.com/gh/watch'


class UnauthorizedException(Exception):
    """Unauthorized user exception"""


async def accept_invitations(
    url='https://api.github.com/user/repository_invitations',
    username=os.environ.get('GITHUB_USER', ''),
    token=os.environ.get('GITHUB_TOKEN', ''),
):

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}',
        'User-Agent': username,
    }

    async with aiohttp.ClientSession(headers=headers) as client:

        logging.info('Retrieving open invitations.')
        async with client.get(url) as response:
            invitations = await response.json()
            if response.status != 200:
                logging.error('Failed to retrieve invitations.')
                return

        if len(invitations) > 0:
            msg = f'Accepting {len(invitations)} open invitations.'
        else:
            msg = 'No open invitations found.'
        logging.info(msg)

        for invitation in invitations:
            repo_name = invitation['repository']['full_name']
            invitation_id = invitation['id']
            async with client.patch(f'{url}/{invitation_id}') as response:
                status = await response.status
                if status == 204:
                    logging.info(f'Successfully accepted invitation to {repo_name}.')
                else:
                    logging.error(f'Failed to accept invitation to {repo_name}.')


async def validate_main_repo(
    url='https://api.github.com/repos/NCAR/xdevbot-testing',
    username=os.environ.get('GITHUB_USER', None),
    token=os.environ.get('GITHUB_TOKEN', None),
):

    main_repo = await get_main_repo(url, username=username, token=token)

    main_hook = await get_main_hook(
        main_repo['hooks_url'],
        create=main_repo['permissions']['admin'],
        username=username,
        token=token,
    )

    project_url = f"{main_repo['url']}/projects"
    main_project = await get_main_project(
        project_url, create=main_repo['permissions']['admin'], username=username, token=token
    )

    logging.info('Writing main repository data to file.')
    db_main = {'repo': main_repo, 'hook': main_hook, 'board': main_project}
    with open('database.json', 'w') as db:
        json.dump(db_main, db, indent=3)


async def get_main_repo(
    url, username=os.environ.get('GITHUB_USER', None), token=os.environ.get('GITHUB_TOKEN', None)
):

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}',
        'User-Agent': username,
    }

    async with aiohttp.ClientSession(headers=headers) as client:

        logging.info('Retrieving main repository metadata.')
        async with client.get(url) as response:
            main_repo = await response.json()

    return main_repo


async def get_main_hook(
    url,
    create=True,
    username=os.environ.get('GITHUB_USER', None),
    token=os.environ.get('GITHUB_TOKEN', None),
):

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}',
        'User-Agent': username,
    }

    async with aiohttp.ClientSession(headers=headers) as client:

        logging.info('Retrieving main repository webhooks.')
        async with client.get(url) as response:
            hooks = await response.json()

        potl_hooks = []
        for hook in hooks:
            if (
                hook['events'] == ['project_card']
                and hook['config']['url'] == XDEVBOT_MAIN_ENDPOINT
                and hook['config']['content_type'] == 'json'
                and hook['active']
            ):
                potl_hooks.append(hook)

        if len(potl_hooks) > 0:
            msg = f'Found {len(potl_hooks)} potential main repository webhooks.'
        else:
            msg = 'No potential main repository webhooks found.'
        logging.debug(msg)

        if len(potl_hooks) == 0:
            if create:
                logging.info('Creating main repository webhook.')
                request = dict(
                    name='web',
                    events=['project_card'],
                    config=dict(url=XDEVBOT_MAIN_ENDPOINT, content_type='json'),
                )
                async with client.post(url, json=request) as response:
                    main_hook = await response.json()
                    if response.status != 201:
                        logging.error('Failed to create main repository webhook.')
            else:
                msg = 'No main repository webhook found.'
                logging.error(msg)
                raise UnauthorizedException(msg)
        elif len(potl_hooks) == 1:
            logging.info('Existing main repository webhook found.')
            main_hook = potl_hooks[0]
        else:
            timestamps = [
                datetime.strptime(hook['updated_at'], '%Y-%m-%dT%H:%M:%SZ') for hook in potl_hooks
            ]
            newest_timestamp, i_hook = max((t, i) for (i, t) in enumerate(timestamps))[1]
            logging.info(
                f'Found {len(potl_hooks)} potential webhooks on the main repository, '
                f'choosing most recent webhook at {newest_timestamp}.'
            )
            main_hook = potl_hooks[i_hook]

    return main_hook


async def get_main_project(
    url,
    create=True,
    username=os.environ.get('GITHUB_USER', None),
    token=os.environ.get('GITHUB_TOKEN', None),
):

    project_name = 'Xdevbot Main Project'
    project_description = 'Main Project Board for the NCAR Experimental Development Team'
    project_columns = ['To Do', 'Priority', 'In Progress', 'Waiting', 'Done']

    headers = {
        'Accept': 'application/vnd.github.inertia-preview+json',
        'Authorization': f'token {token}',
        'User-Agent': username,
    }

    async with aiohttp.ClientSession(headers=headers) as client:

        logging.info('Searching for main project board')
        async with client.get(url) as response:
            projects = await response.json()

        potl_projects = []
        for project in projects:
            if project['name'] == project_name and project['body'] == project_description:
                potl_projects.append(project)

        if len(potl_projects) == 0:
            if create:
                logging.info('Creating main project board.')
                request = dict(name=project_name, body=project_description)
                async with client.post(url, json=request) as response:
                    main_project = await response.json()

                url = main_project['columns_url']
                main_columns = []
                for column in project_columns:
                    async with client.post(url, json={'name': column}) as response:
                        main_column = await response.json()
                    main_columns.append(main_column)
            else:
                msg = 'No main project board found.'
                logging.error(msg)
                raise UnauthorizedException(msg)
        elif len(potl_projects) == 1:
            logging.info('Existing main project board found.')
            main_project = potl_projects[0]

            url = main_project['columns_url']
            async with client.get(url) as response:
                main_columns = await response.json()
        else:
            msg = 'Multiple main project boards found with same name.'
            logging.error(msg)
            raise NotImplementedError(msg)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(accept_invitations())
    loop.run_until_complete(validate_main_repo())
    loop.close()
