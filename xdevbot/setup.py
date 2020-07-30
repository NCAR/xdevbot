import logging
import os

import pandas as pd
import yaml
from aiohttp import ClientSession, ClientTimeout

from xdevbot import queries, utils


async def setup(app):
    app['github_username'] = os.environ.get('GITHUB_USER', None)
    app['github_token'] = os.environ.get('GITHUB_TOKEN', None)

    config = await get_config()
    logging.info('Configuration file read')
    app['config'] = build_config_frame(config)

    projects = await query_projects(token=app['github_token'])
    logging.info('Projects data read')
    app['cards'] = build_cards_frame(projects)
    app['columns'] = build_columns_map(projects)


async def get_config(
    url='https://raw.githubusercontent.com/NCAR/xdev/master/xdevbot.yaml', timeout=60,
):
    timeout = ClientTimeout(total=timeout)
    async with ClientSession(timeout=timeout) as session:
        response = await session.get(url)
    if response.status != 200:
        raise RuntimeError(f'Failed to read config file: {response.status}')
    text = await response.text()
    return yaml.safe_load(text)


def build_config_frame(config):
    data = {'project_url': [], 'repo': []}
    for name in config:
        url = config[name]['url']
        repos = config[name]['repos']
        if repos:
            for repo in config[name]['repos']:
                data['project_url'].append(url)
                data['repo'].append(repo)

    return pd.DataFrame(data=data)


async def query_projects(token=None, timeout=60, check_limits=True):
    headers = {}
    if token:
        headers['Authorization'] = f'bearer {token}'
    url = 'https://api.github.com/graphql'
    timeout = ClientTimeout(total=timeout)
    json = {'query': queries.GET_ALL_CARDS}

    async with ClientSession(headers=headers, timeout=timeout) as session:
        response = await session.post(url=url, json=json)
    if response.status != 200:
        raise RuntimeError(f'Failed to read project data: {response.status}')
    data = await response.json()

    if check_limits:
        await utils.check_rate_limits(kind='graphql', token=token)

    return data['data']['repository']


def build_cards_frame(projects):
    data = {'card_id': [], 'note': [], 'creator': [], 'column_id': [], 'project_url': []}
    for project in projects['projects']['nodes']:
        url = project['url']
        for column in project['columns']['nodes']:
            column_id = column['databaseId']
            for card in column['cards']['nodes']:
                card_id = card['databaseId']
                note = card['note']
                creator = card['creator']['login']

                data['card_id'].append(card_id)
                data['note'].append(note)
                data['creator'].append(creator)
                data['column_id'].append(column_id)
                data['project_url'].append(url)
    return pd.DataFrame(data=data)


def build_columns_map(projects):
    columns = {}
    for project in projects['projects']['nodes']:
        url = project['url']
        columns[url] = {}
        for column in project['columns']['nodes']:
            name = column['name']
            column_id = column['databaseId']
            columns[url][name] = column_id
    return columns
