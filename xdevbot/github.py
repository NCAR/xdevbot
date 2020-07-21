from fastapi import HTTPException, Request, status

_ROUTING = {}


async def Event(request: Request):
    kind = request.headers.get('X-GitHub-Event', None)
    guid = request.headers.get('X-GitHub-Delivery', None)
    signature = request.headers.get('X-Hub-Signature', None)
    user_agent = request.headers.get('User-Agent', None)
    if not user_agent.startswith('GitHub-Hookshot/'):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='User agent looks incorrect'
        )
    content_type = request.headers.get('Content-Type', None)
    if not content_type == 'application/json':
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail='Unsupported media type'
        )
    payload = await request.json()
    action = payload.get('action', None)
    return EventType(
        kind=kind,
        guid=guid,
        signature=signature,
        user_agent=user_agent,
        content_type=content_type,
        payload=payload,
        action=action,
    )


class EventType:
    """A simple wrapper on a FastAPI Request Object for GitHub Webhook Event Payloads"""

    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])


def router(event: EventType):
    if event.kind in _ROUTING and event.action in _ROUTING[event.kind]:
        return _ROUTING[event.kind][event.action]
    else:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail='GitHub route undefined'
        )


class route:
    """A decorator that maps a specific GitHub event+action with a function"""

    def __init__(self, kind, action):
        self.kind = kind
        self.action = action

    def __call__(self, f):
        if self.kind not in _ROUTING:
            _ROUTING[self.kind] = {}
        _ROUTING[self.kind][self.action] = f
        return f
