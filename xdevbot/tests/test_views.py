from bs4 import BeautifulSoup

from ..cli import init_app


async def test_index(aiohttp_client, loop):
    app = await init_app()
    client = await aiohttp_client(app)

    resp = await client.get('/')
    assert resp.status == 200
    html_doc = await resp.text()
    soup = BeautifulSoup(html_doc, 'html.parser')
    assert soup.title.string == 'Xdevbot'

    resp = await client.post('/', data={})
    assert resp.status == 200
    html_doc = await resp.text()
    soup = BeautifulSoup(html_doc, 'html.parser')
    assert soup.title.string == '404 Page Not Found'


async def test_ghmain(aiohttp_client, loop):
    app = await init_app()
    client = await aiohttp_client(app)

    resp = await client.get('/gh/main')
    assert resp.status == 200
    html_doc = await resp.text()
    soup = BeautifulSoup(html_doc, 'html.parser')
    assert soup.title.string == '404 Page Not Found'

    resp = await client.post('/gh/main', data={})
    assert resp.status == 200
    html_doc = await resp.text()
    soup = BeautifulSoup(html_doc, 'html.parser')
    assert soup.text == 'OK'


async def test_ghwatch(aiohttp_client, loop):
    app = await init_app()
    client = await aiohttp_client(app)

    resp = await client.get('/gh/watch')
    assert resp.status == 200
    html_doc = await resp.text()
    soup = BeautifulSoup(html_doc, 'html.parser')
    assert soup.title.string == '404 Page Not Found'

    resp = await client.post('/gh/watch', data={})
    assert resp.status == 200
    html_doc = await resp.text()
    soup = BeautifulSoup(html_doc, 'html.parser')
    assert soup.text == 'OK'
