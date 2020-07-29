import logging
import os

import yaml
from aiohttp import ClientSession, ClientTimeout

from xdevbot.utils import check_graphql_rate_limits, squash_graphql_response


async def setup(app):
    config = {}
    config['github_username'] = os.environ.get('GITHUB_USER', None)
    config['github_token'] = os.environ.get('GITHUB_TOKEN', None)
    config['projects'] = await get_projects_config()
    logging.info('Configuration file read')
    app['config'] = config

    graphql_response = await query_projects_data(token=config['github_token'])
    logging.info('Project data read')
    data = squash_graphql_response(graphql_response)
    app['projects'] = filter_projects(data['projects'], config=config['projects'])


async def get_projects_config(
    url='https://raw.githubusercontent.com/NCAR/xdev/master/xdevbot.yaml', timeout=60,
):
    timeout = ClientTimeout(total=timeout)
    async with ClientSession(timeout=timeout) as session:
        response = await session.get(url)
    if response.status != 200:
        raise RuntimeError(f'Failed to read config file: {response.status}')
    text = await response.text()
    return yaml.safe_load(text)


async def query_projects_data(token=None, timeout=60):
    headers = {'Content-Type': ''}
    if token:
        headers['Authorization'] = f'bearer {token}'
    url = 'https://api.github.com/graphql'
    query = """query {
    repository(name: \"xdev\", owner: \"NCAR\") {
        projects(first: 9) { edges { node {
            url
            databaseId
            columns(first: 7) { edges { node {
                name
                databaseId
                cards(first: 100) { edges { node {
                    databaseId
                    note
                    creator { login }
                }}}
            }}}
        }}}
    }
    rateLimit {
        cost
        limit
        remaining
    }
}"""
    timeout = ClientTimeout(total=timeout)
    async with ClientSession(headers=headers, timeout=timeout) as session:
        response = await session.post(url=url, json={'query': query})
    if response.status != 200:
        raise RuntimeError(f'Failed to read project data: {response.status}')
    data = await response.json()

    check_graphql_rate_limits(data['data']['rateLimit'])

    return data['data']['repository']


def filter_projects(projects, config={}):
    config_urls = set(config[project]['url'] for project in config)
    filtered = {}
    for project in projects:
        url = projects[project]['url']
        if url in config_urls:
            filtered[project] = projects[project]
    return filtered
