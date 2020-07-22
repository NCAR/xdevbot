from aiohttp import web

import xdevbot.github as gh


async def api(request: web.Request):
    event = await gh.Event(request)
    handler = gh.router(event)
    return await handler(event)


async def init_app():
    app = web.Application()

    app.router.add_post('/', api)

    return app


@gh.route('issues', 'created')
async def issue_created(event: gh.EventType):
    return web.Response(text='Thanks!')
