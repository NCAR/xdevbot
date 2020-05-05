import aiohttp_jinja2
from aiohttp import web

# === HTTP/GET ============================================


@aiohttp_jinja2.template('home.html.j2')
async def home(request):
    return {'title': 'Xdevbot'}


@aiohttp_jinja2.template('auth.html.j2')
async def auth(request):
    return {}


@aiohttp_jinja2.template('setup.html.j2')
async def setup(request):
    return {}


# === HTTP/POST ===========================================


@aiohttp_jinja2.template('github.html.j2')
async def github(request):
    return web.Response(text='OK')
