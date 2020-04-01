from aiohttp import web
from bs4 import BeautifulSoup

from ..cli import init_app


async def test_404(aiohttp_client, loop):
    app = await init_app()
    client = await aiohttp_client(app)
    resp = await client.get('*&!@#$%')
    assert resp.status == 200

    html_doc = await resp.text()
    soup = BeautifulSoup(html_doc, 'html.parser')
    assert soup.title.string == '404 Page Not Found'


async def test_500(aiohttp_client, loop):
    app = await init_app()

    async def error(request):
        raise web.HTTPInternalServerError()

    app.router.add_get('/error', error)

    client = await aiohttp_client(app)
    resp = await client.get('/error')
    assert resp.status == 200

    html_doc = await resp.text()
    soup = BeautifulSoup(html_doc, 'html.parser')
    assert soup.title.string == '500 Internal Server Error'
