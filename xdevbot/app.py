import logging
import sys

from aiohttp import web

from xdevbot import github
from xdevbot.utils import check_rate_limits

LOGFMT = '%(asctime)s: %(levelname)s: %(message)s'
DTFMT = '%Y-%m-%d %H:%M:%S'


async def init_app(token=None, loglevel='INFO'):
    logger = logging.getLogger('app')
    formatter = logging.Formatter(LOGFMT, datefmt=DTFMT)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, loglevel.upper()))
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logging.info('Beginning application initialization')

    app = web.Application()
    app['logger'] = logger
    app['token'] = token
    app.router.add_post('/hooks/github/', github.handler)

    logging.info('Application initialization complete')
    await check_rate_limits(kind='core', token=app['token'])
    await check_rate_limits(kind='graphql', token=app['token'])

    return app
