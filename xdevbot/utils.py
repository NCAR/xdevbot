import logging

from aiohttp import ClientSession


def repo_fullname_from_url(url: str) -> str:
    return '/'.join(url.split('/')[-2:])


def squash_graphql_response(obj, key: str = 'databaseId'):
    if isinstance(obj, dict):
        squashed = {}
        for k in obj:
            if k == 'edges':
                for edge in obj['edges']:
                    node = edge['node']
                    k_ = node.pop(key)
                    squashed[k_] = squash_graphql_response(node, key=key)
            else:
                squashed[k] = squash_graphql_response(obj[k], key=key)
        return squashed
    else:
        return obj


async def check_rate_limits(kind: str = 'core', username: str = None, token: str = None) -> None:
    headers = {'Content-Type': 'application/json'}
    if username:
        headers['User-Agent'] = username
    if token:
        headers['Authorization'] = f'token {token}'
    async with ClientSession(headers=headers) as session:
        response = await session.get('https://api.github.com/rate_limit')
    if response.status == 200:
        rates = await response.json()
        remaining = rates['resources'][kind]['remaining']
        limit = rates['resources'][kind]['limit']
        logging.info(f'{kind.capitalize()} Rate Limit: {remaining} requests remaining of {limit}')
    else:
        logging.warning(f'Failed to retrieve rate limits: {response.status}')
