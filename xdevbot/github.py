from collections import defaultdict
from typing import Callable, Mapping

from aiohttp import ClientSession, ClientTimeout, web

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
    kind = request.headers.get('X-GitHub-Event', None)
    element = 'issue' if kind == 'issues' else kind
    return EventType(
        app=request.app,
        kind=kind,
        element=element,
        guid=request.headers.get('X-GitHub-Delivery', None),
        signature=request.headers.get('X-Hub-Signature', None),
        user_agent=user_agent,
        content_type=content_type,
        payload=payload,
        action=payload.get('action', None),
    )


async def handler(request: web.Request) -> web.Response:
    event = await Event(request)
    handler = router(event)
    return await handler(event)


def router(event: EventType) -> Callable:
    if event.kind in _ROUTING and event.action in _ROUTING[event.kind]:
        return _ROUTING[event.kind][event.action]
    else:

        async def _not_implemented(event: EventType):
            return web.Response()

        return _not_implemented


class route:
    """A decorator that maps a specific GitHub event+action with a function"""

    def __init__(self, kind: str, action: str):
        self._kind = kind
        self._action = action

    def __call__(self, func):
        _ROUTING[self._kind][self._action] = func
        return func


class ProjectClientSession:
    """A class that provides a simple client session for GitHub actions"""

    def __init__(self, headers={}, token=None) -> 'ProjectClientSession':
        headers['Accept'] = 'application/vnd.github.inertia-preview+json'
        headers['User-Agent'] = 'xdevbot'
        if token:
            headers['Authorization'] = f'token {token}'
        self.headers = headers

    async def __aenter__(self):
        self._session = ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
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

    async def create_project_card(self, note: str, column_id: int) -> web.Response:
        url = f'https://api.github.com/projects/columns/{column_id}/cards'
        data = {'note': note}
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
    timeout = ClientTimeout(total=timeout)
    async with ClientSession(headers=headers, timeout=timeout) as session:
        response = await session.post(url=url, json=json)
    if response.status != 200:
        raise RuntimeError(f'Failed to read project data: {response.status}')
    return await response.json()
