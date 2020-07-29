from typing import Callable

from aiohttp import web, ClientSession

_ROUTING = {}


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
    return EventType(
        app=request.app,
        kind=request.headers.get('X-GitHub-Event', None),
        guid=request.headers.get('X-GitHub-Delivery', None),
        signature=request.headers.get('X-Hub-Signature', None),
        user_agent=user_agent,
        content_type=content_type,
        payload=payload,
        action=payload.get('action', None),
    )


async def handler(request: web.Request):
    event = await Event(request)
    handler = router(event)
    return await handler(event)


def router(event: EventType) -> Callable:
    if event.kind in _ROUTING and event.action in _ROUTING[event.kind]:
        return _ROUTING[event.kind][event.action]
    else:
        raise web.HTTPNotImplemented(reason='GitHub route undefined')


class route:
    """A decorator that maps a specific GitHub event+action with a function"""

    def __init__(self, kind, action):
        self.kind = kind
        self.action = action

    def __call__(self, f: Callable) -> Callable:
        if self.kind not in _ROUTING:
            _ROUTING[self.kind] = {}
        _ROUTING[self.kind][self.action] = f
        return f


class ProjectClientSession(ClientSession):
    """A class that provides a simple client session for GitHub actions"""

    def __init__(self, *args, **kwargs) -> 'ProjectClientSession':
        username = kwargs.pop('username', None)
        token = kwargs.pop('token', None)
        headers = kwargs.pop('headers', {})
        headers['Accept'] = 'application/vnd.github.inertia-preview+json'
        if username:
            headers['User-Agent'] = username
        if token:
            headers['Authorization'] = f'token {token}'
        kwargs['headers'] = headers
        super().__init__(*args, **kwargs)

    async def list_project_cards(self, column_id: int, archived_state: str = 'not_archived') -> web.Response:
        url = f'https://api.github.com/projects/columns/{column_id}/cards'
        data = {'archived_state': archived_state}
        return await self.get(url, json=data)

    async def get_project_card(self, card_id: int) -> web.Response:
        url = f'https://api.github.com/projects/columns/cards/{card_id}'
        return await self.get(url)

    async def create_project_card(self, note: str, column_id: int) -> web.Response:
        url = f'https://api.github.com/projects/columns/{column_id}/cards'
        data = {'note': note}
        return await self.post(url, json=data)

    async def update_project_card(self, card_id: int, archived: bool = True) -> web.Response:
        url = f'https://api.github.com/projects/columns/cards/{card_id}'
        data = {'archived': archived}
        return await self.patch(url, json=data)

    async def delete_project_card(self, card_id: int) -> web.Response:
        url = f'https://api.github.com/projects/columns/cards/{card_id}'
        return await self.delete(url)

    async def move_project_card(self, card_id: int, column_id: int, position: str = 'top') -> web.Response:
        url = f'https://api.github.com/projects/columns/cards/{card_id}/moves'
        data = {'position': position, 'column_id': column_id}
        return await self.post(url, json=data)
