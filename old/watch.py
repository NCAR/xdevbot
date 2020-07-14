import asyncio
import json
import logging
import os
from datetime import datetime

import aiohttp

logging.basicConfig(level=logging.INFO)

XDEVBOT_WATCH_ENDPOINT = 'http://xdevbot.herokuapp.com/gh/watch'


class InvalidRequest(Exception):
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


async def get_watch_list(
    url='https://api.github.com/user/repos',
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

        logging.info('Retrieving watch list.')
        repos = []
        async with client.get(url, params={'visibility': 'public'}) as response:
            repos.extend(await response.json())
            if response.status != 200:
                msg = 'Could not retrieve accessible repositories'
                logging.error(msg)
                raise InvalidRequest(msg)

        async with client.get(url, params={'visibility': 'private'}) as response:
            repos.extend(await response.json())
            if response.status != 200:
                msg = 'Could not retrieve accessible repositories'
                logging.error(msg)
                raise InvalidRequest(msg)

        watchable_repos = [repo for repo in repos if repo['permissions']['admin']]

        for repo in watchable_repos:
            full_name = repo['full_name']
            hooks_url = repo['hooks_url']

            async with client.get(hooks_url) as response:
                hooks = await response.json()
                if response.status != 200:
                    msg = f'Could not retrieve webhooks on repository {full_name}'
                    logging.error(msg)
                    raise InvalidRequest(msg)

            potl_hooks = []
            for hook in hooks:
                if (
                    set(hook['events']) == set(['issues', 'pull_request'])
                    and hook['config']['url'] == XDEVBOT_WATCH_ENDPOINT
                    and hook['config']['content_type'] == 'json'
                    and hook['active']
                ):
                    potl_hooks.append(hook)

            if len(potl_hooks) == 0:
                logging.info(f'Creating webhook on repository {full_name}.')
                request = dict(
                    name='web',
                    events=['issues', 'pull_request'],
                    config=dict(url=XDEVBOT_WATCH_ENDPOINT, content_type='json'),
                )
                async with client.post(hooks_url, json=request) as response:
                    hook = await response.json()
                    if response.status != 201:
                        hook = None
                        logging.error(f'Failed to create webhook on repository {full_name}.')
            elif len(potl_hooks) == 1:
                hook = potl_hooks[0]
                logging.info(f'Existing webhook found on repository {full_name}.')
            else:
                timestamps = [
                    datetime.strptime(hook['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
                    for hook in potl_hooks
                ]
                newest_timestamp, i_hook = max((t, i) for (i, t) in enumerate(timestamps))[1]
                logging.info(
                    f'Found {len(potl_hooks)} potential webhooks on repository {full_name}, '
                    f'choosing most recent webhook at {newest_timestamp}.'
                )
                hook = potl_hooks[i_hook]

            if hook is not None:
                database[full_name] = {'repo': repo, 'hook': hook}


if __name__ == '__main__':
    database = {}

    loop = asyncio.get_event_loop()
    loop.run_until_complete(accept_invitations())
    loop.run_until_complete(get_watch_list(database=database))
    loop.close()

    logging.info('Writing main repository data to file.')
    with open('watch_database.json', 'w') as db:
        json.dump(database, db, indent=3)
