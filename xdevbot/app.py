import logging

from aiohttp import web

from xdevbot import routes
from xdevbot.utils import log_rate_limits

logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(handler)


async def init_app(token: str = None, loglevel: str = 'INFO'):
    logger.setLevel(getattr(logging, loglevel.upper()))

    if token is None:
        logger.warning('GitHub token not set!')

    app = web.Application()
    app['token'] = token
    app.router.add_post('/hooks/github/', routes.github_handler)

    logger.info('Application initialization complete')
    await log_rate_limits(kind=['core', 'graphql'], token=app['token'])

    return app
