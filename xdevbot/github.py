from fastapi import Response, status

_ROUTING = {}


def router(event=None, action=None):
    if event in _ROUTING and action in _ROUTING[event]:
        return _ROUTING[event][action]
    else:
        return no_route_function


def no_route_function(payload={}, guid=None, signature=None):
    return Response(status_code=status.HTTP_501_NOT_IMPLEMENTED)


class route:
    """A decorator that maps a specific GitHub event+action with a function"""

    def __init__(self, event, action):
        self.event = event
        self.action = action

    def __call__(self, f):
        if self.event not in _ROUTING:
            _ROUTING[self.event] = {}
        _ROUTING[self.event][self.action] = f
        return f


@route('issues', 'created')
def issue_created(payload={}, guid=None, signature=None):
    return Response(status_code=200)
