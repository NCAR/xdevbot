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


async def test_github(aiohttp_client, loop):
    app = await init_app()
    client = await aiohttp_client(app)

    resp = await client.get('/github')
    assert resp.status == 200
    html_doc = await resp.text()
    soup = BeautifulSoup(html_doc, 'html.parser')
    assert soup.title.string == '404 Page Not Found'

    resp = await client.post('/github', data={})
    assert resp.status == 200
    html_doc = await resp.text()
    soup = BeautifulSoup(html_doc, 'html.parser')
    assert soup.text == 'OK'
