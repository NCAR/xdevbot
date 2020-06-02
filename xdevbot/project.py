import asyncio
import json
import logging
import os
from datetime import datetime

import aiohttp

logging.basicConfig(level=logging.INFO)

MAIN_REPO_URL = 'https://api.github.com/repos/NCAR/xdevbot-testing'
XDEVBOT_MAIN_ENDPOINT = 'http://xdevbot.herokuapp.com/gh/main'


class InvalidRequest(Exception):
    """Invalid request exception"""


async def get_main_repo(
    url,
    database={},
    username=os.environ.get('GITHUB_USER', ''),
    token=os.environ.get('GITHUB_TOKEN', ''),
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

            if response.status == 200:
                database['repo'] = main_repo
            else:
                logging.error('Could not retrieve main repository metadata.')


async def get_main_hook(
    url,
    create=True,
    database={},
    username=os.environ.get('GITHUB_USER', ''),
    token=os.environ.get('GITHUB_TOKEN', ''),
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
            if response.status != 200:
                msg = 'Could not retrieve main repository webhooks'
                logging.error(msg)
                raise InvalidRequest(msg)

        potl_hooks = []
        for hook in hooks:
            if (
                hook['events'] == ['project_card']
                and hook['config']['url'] == XDEVBOT_MAIN_ENDPOINT
                and hook['config']['content_type'] == 'json'
                and hook['active']
            ):
                potl_hooks.append(hook)

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
                raise InvalidRequest(msg)
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

    database['hook'] = main_hook


async def get_main_project(
    url,
    database={},
    create=True,
    username=os.environ.get('GITHUB_USER', ''),
    token=os.environ.get('GITHUB_TOKEN', ''),
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
            if response.status != 200:
                msg = 'Could not find main project board'
                logging.error(msg)
                raise InvalidRequest(msg)

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
                    if response.status != 201:
                        msg = 'Could not create main project board'
                        logging.error(msg)
                        raise InvalidRequest(msg)

                url = main_project['columns_url']
                main_columns = []
                for column in project_columns:
                    async with client.post(url, json={'name': column}) as response:
                        main_column = await response.json()
                        if response.status != 201:
                            msg = f'Could not create main project column {column}'
                            logging.error(msg)
                            raise InvalidRequest(msg)
                    main_columns.append(main_column)
            else:
                msg = 'No main project board found.'
                logging.error(msg)
                raise InvalidRequest(msg)
        elif len(potl_projects) == 1:
            logging.info('Existing main project board found.')
            main_project = potl_projects[0]

            url = main_project['columns_url']
            async with client.get(url) as response:
                main_columns = await response.json()
                if response.status != 200:
                    msg = 'Could not get main project columns'
                    logging.error(msg)
                    raise InvalidRequest(msg)
        else:
            msg = 'Multiple main project boards found with same name.'
            logging.error(msg)
            raise NotImplementedError(msg)

    database['project'] = main_project
    database['columns'] = main_columns


if __name__ == '__main__':
    database = {}

    loop = asyncio.get_event_loop()

    loop.run_until_complete(get_main_repo(MAIN_REPO_URL, database=database))

    hooks_url = database['repo']['hooks_url']
    projects_url = f"{database['repo']['url']}/projects"
    create = database['repo']['permissions']['admin']

    tasks = [
        loop.create_task(get_main_hook(hooks_url, create=create, database=database)),
        loop.create_task(get_main_project(projects_url, create=create, database=database)),
    ]
    loop.run_until_complete(asyncio.gather(*tasks))

    loop.close()

    logging.info('Writing main repository data to file.')
    with open('project_database.json', 'w') as db:
        json.dump(database, db, indent=3)
