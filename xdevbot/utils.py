import logging


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


def check_graphql_rate_limits(limits: dict) -> None:
    query_cost = limits['cost']
    if query_cost > 1:
        logging.warning(f'Projects data query unexpectedly large ({query_cost} points)')
    query_remaining = limits['remaining']
    query_limit = limits['limit']
    logging.info(f'Rate Limit: {query_remaining} remaining of {query_limit}')
