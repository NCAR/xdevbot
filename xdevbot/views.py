import aiohttp_jinja2
from aiohttp import web


@aiohttp_jinja2.template('home.html.j2')
async def home(request):
    return {'title': 'Xdevbot'}


async def github(request):
    return web.Response(text='OK')
