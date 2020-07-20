from fastapi import Request, Response, status

from xdevbot.github import router


def init_views(app):
    @app.post('/')
    async def github(request: Request):
        event = request.headers.get('X-GitHub-Event', None)
        guid = request.headers.get('X-GitHub-Delivery', None)
        signature = request.headers.get('X-Hub-Signature', None)
        user_agent = request.headers.get('User-Agent', None)
        content_type = request.headers.get('Content-Type', None)

        if not user_agent.startswith('GitHub-Hookshot/'):
            return Response(status_code=status.HTTP_406_NOT_ACCEPTABLE)

        if not content_type == 'application/json':
            return Response(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        payload = await request.json()
        action = payload.get('action', None)
        handler = router(event=event, action=action)

        return handler(payload=payload, guid=guid, signature=signature)
