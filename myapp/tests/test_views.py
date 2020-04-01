from bs4 import BeautifulSoup

from ..cli import init_app


async def test_index(aiohttp_client, loop):
    app = await init_app()
    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert resp.status == 200
    html_doc = await resp.text()
    soup = BeautifulSoup(html_doc, 'html.parser')
    assert soup.title.string == '[Title]'
