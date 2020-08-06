import logging
import os

from aiohttp import web

from xdevbot import routes
from xdevbot.utils import log_rate_limits

logger = logging.getLogger('gunicorn.error')


async def init_app():
    token = os.environ.get('XDEVBOT_TOKEN', None)
    if token is None:
        logger.warning('GitHub token not set!')

    app = web.Application(logger=logger)
    app['token'] = token
    app.router.add_post('/hooks/github/', routes.github_handler)

    logger.info('Application initialization complete')
    await log_rate_limits(kind=['core', 'graphql'], token=app['token'])

    return app
