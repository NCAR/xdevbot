import asyncio
import logging
import os
from contextlib import suppress

from aiohttp import web

from xdevbot import routes
from xdevbot.polling import polling
from xdevbot.utils import log_rate_limits

glogger = logging.getLogger('gunicorn.error')

logger = logging.getLogger('xdevbot')
logger.setLevel(glogger.level)
formatter = logging.Formatter('[%(levelname)s:%(module)s:%(process)d] %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
level = glogger.handlers[0].level if glogger.handlers else logging.INFO
handler.setLevel(level)
logger.addHandler(handler)


async def init_app():
    token = os.environ.get('XDEVBOT_TOKEN', None)
    if token is None:
        logger.warning('GitHub token not set!')

    app = web.Application(logger=logger)
    app['token'] = token
    app.on_startup.append(startup_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    app.router.add_post('/hooks/github/', routes.github_handler)
    app.router.add_post('/project/hooks/github/', routes.github_handler)

    logger.info('Application initialization complete')
    await log_rate_limits(category=['core', 'graphql'], token=app['token'])

    return app


async def startup_background_tasks(app):
    gunicorn_nworkers = int(os.environ.get('GUNICORN_NUM_WORKERS', 0))
    gunicorn_workerid = int(os.environ.get('GUNICORN_WORKER_ID', 0))

    global_period = 10
    worker_period = global_period * gunicorn_nworkers
    worker_offset = (gunicorn_workerid - 1) * global_period
    await asyncio.sleep(worker_offset)

    app['polling'] = asyncio.create_task(polling(period=worker_period, token=app['token']))


async def cleanup_background_tasks(app):
    app['polling'].cancel()
    with suppress(asyncio.CancelledError):
        await app['polling']
