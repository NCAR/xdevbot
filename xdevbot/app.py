from aiohttp import web

from xdevbot import routes
from xdevbot.utils import get_rate_limits

LOGFMT = '%(asctime)s: %(levelname)s: %(message)s'
DTFMT = '%Y-%m-%d %H:%M:%S'


async def init_app(token=None, loglevel='INFO'):
    app = web.Application()
    app['token'] = token
    app.router.add_post('/hooks/github/', routes.handler)

    print('Application initialization complete')
    rates = await get_rate_limits(token=app['token'])
    print(f"Core Rate Limits: {rates['core']['remaining']} remaining of {rates['core']['limit']}")
    print(
        f"GraphQL Rate Limits: {rates['graphql']['remaining']} remaining of {rates['graphql']['limit']}"
    )

    return app
