import logging
from collections import defaultdict
from typing import Callable, Mapping

from aiohttp import ClientSession, ClientTimeout, web

from xdevbot import utils

logger = logging.getLogger('gunicorn.error')

_ROUTING = defaultdict(dict)


class EventType:
    """A simple wrapper on a FastAPI Request Object for GitHub Webhook Event Payloads"""

    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])


async def Event(request: web.Request) -> EventType:
    user_agent = request.headers.get('User-Agent', None)
    if not user_agent.startswith('GitHub-Hookshot/'):
        raise web.HTTPNotAcceptable(reason='User agent looks incorrect')
    content_type = request.headers.get('Content-Type', None)
    if not content_type == 'application/json':
        raise web.HTTPUnsupportedMediaType(reason='Not a JSON payload')
    payload = await request.json()
    event_type = request.headers.get('X-GitHub-Event', None)
    key = 'issue' if event_type == 'issues' else event_type
    return EventType(
        app=request.app,
        key=key,
        type=event_type,
        guid=request.headers.get('X-GitHub-Delivery', None),
        signature=request.headers.get('X-Hub-Signature', None),
        user_agent=user_agent,
        content_type=content_type,
        payload=payload,
        action=payload.get('action', None),
    )


async def route_not_implemented(event: EventType) -> web.Response:
    return web.Response()


def router(event: EventType) -> Callable:
    if event.type in _ROUTING and event.action in _ROUTING[event.type]:
        logger.debug(f'GitHub route found [{event.type}/{event.action}]')
        return _ROUTING[event.type][event.action]
    else:
        logger.debug(f'Failed to find GitHub route [{event.type}/{event.action}]')

        return route_not_implemented


class route:
    """A decorator that maps a specific GitHub event+action with a function"""

    def __init__(self, type: str, action: str) -> 'route':
        self._type = type
        self._action = action

    def __call__(self, func: Callable) -> Callable:
        _ROUTING[self._type][self._action] = func
        return func


class IssueClientSession:
    """A class that provides a simple client session for GitHub actions"""

    def __init__(
        self, headers: dict = {}, token: str = None, timeout: int = 60
    ) -> 'IssueClientSession':
        headers['Accept'] = 'application/vnd.github.v3+json'
        headers['User-Agent'] = 'xdevbot'
        if token:
            headers['Authorization'] = f'token {token}'
        self.token = token
        self.headers = headers
        self.timeout = timeout

    async def __aenter__(self):
        timeout = ClientTimeout(total=self.timeout)
        self._session = ClientSession(headers=self.headers, timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._session.close()
        await utils.log_rate_limits(token=self.token)
        return self

    async def get_issue(self, owner: str, repo: str, number: int) -> web.Response:
        url = f'https://api.github.com/repos/{owner}/{repo}/issues/{number}'
        return await self._session.get(url)


class ProjectClientSession:
    """A class that provides a simple client session for GitHub actions"""

    def __init__(
        self, headers: dict = {}, token: str = None, timeout: int = 60
    ) -> 'ProjectClientSession':
        headers['Accept'] = 'application/vnd.github.inertia-preview+json'
        headers['User-Agent'] = 'xdevbot'
        if token:
            headers['Authorization'] = f'token {token}'
        self.token = token
        self.headers = headers
        self.timeout = timeout

    async def __aenter__(self):
        timeout = ClientTimeout(total=self.timeout)
        self._session = ClientSession(headers=self.headers, timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._session.close()
        await utils.log_rate_limits(token=self.token)
        return self

    async def list_project_cards(
        self, column_id: int, archived_state: str = 'not_archived'
    ) -> web.Response:
        url = f'https://api.github.com/projects/columns/{column_id}/cards'
        data = {'archived_state': archived_state}
        return await self._session.get(url, json=data)

    async def get_project_card(self, card_id: int) -> web.Response:
        url = f'https://api.github.com/projects/columns/cards/{card_id}'
        return await self._session.get(url)

    async def create_project_card(
        self, content_id: int, content_type: str, column_id: int
    ) -> web.Response:
        url = f'https://api.github.com/projects/columns/{column_id}/cards'
        data = {'content_id': content_id, 'content_type': content_type}
        return await self._session.post(url, json=data)

    async def update_project_card(self, card_id: int, archived: bool = True) -> web.Response:
        url = f'https://api.github.com/projects/columns/cards/{card_id}'
        data = {'archived': archived}
        return await self._session.patch(url, json=data)

    async def delete_project_card(self, card_id: int) -> web.Response:
        url = f'https://api.github.com/projects/columns/cards/{card_id}'
        return await self._session.delete(url)

    async def move_project_card(
        self, card_id: int, column_id: int, position: str = 'top'
    ) -> web.Response:
        url = f'https://api.github.com/projects/columns/cards/{card_id}/moves'
        data = {'position': position, 'column_id': column_id}
        return await self._session.post(url, json=data)


async def graphql_query(query: str, token: str = None, timeout: int = 60) -> Mapping:
    url = 'https://api.github.com/graphql'
    json = {'query': query}

    headers = {}
    if token:
        headers['Authorization'] = f'bearer {token}'
    tout = ClientTimeout(total=timeout)
    async with ClientSession(headers=headers, timeout=tout) as session:
        response = await session.post(url=url, json=json)
        if response.status != 200:
            raise RuntimeError(f'Failed to read project data: {response.status}')
        data = await response.json()
    await utils.log_rate_limits(category='graphql', token=token, timeout=timeout)
    return data
