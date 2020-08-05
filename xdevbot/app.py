import logging

from aiohttp import web

from xdevbot import github
from xdevbot.utils import check_rate_limits

LOG_FMT = '%(asctime)s: %(levelname)s: %(message)s'
DT_FMT = '%Y-%m-%d %H:%M:%S'


async def init_app(token=None):
    logging.basicConfig(format=LOG_FMT, datefmt=DT_FMT, level=logging.INFO)
    logging.info('Beginning application initialization')

    app = web.Application()
    app['token'] = token
    app.router.add_post('/hooks/github/', github.handler)

    logging.info('Application initialization complete')
    await check_rate_limits(kind='core', token=app['token'])
    await check_rate_limits(kind='graphql', token=app['token'])

    return app
