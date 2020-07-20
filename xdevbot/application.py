from fastapi import FastAPI, Request

import xdevbot.github as gh


def init_app():
    app = FastAPI()

    @app.post('/')
    async def api(request: Request):
        event = await gh.Event(request)
        handler = gh.router(event)
        return handler(event)

    return app


@gh.route('issues', 'created')
def issue_created(event: gh.EventType):
    return {'detail': 'Thanks!'}
