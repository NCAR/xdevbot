import logging

from aiohttp import web

from xdevbot.views import github
from xdevbot.setup import setup


async def init_app():
    app = web.Application()
    logging.basicConfig(
        format='%(asctime)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO
    )
    logging.info('Initializing application')

    await setup(app)
    app.router.add_post('/hooks/github/', github.handler)
    return app
