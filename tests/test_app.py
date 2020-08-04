import pytest
from aiohttp import web

from xdevbot.app import init_app


@pytest.fixture
async def app():
    return await init_app()


async def test_404(app, aiohttp_client, loop):
    client = await aiohttp_client(app)
    resp = await client.get('/unknown')
    assert resp.status == 404
    text = await resp.text()
    assert text == '404: Not Found'


async def test_405(app, aiohttp_client, loop):
    client = await aiohttp_client(app)
    resp = await client.get('/hooks/github/')
    assert resp.status == 405
    text = await resp.text()
    assert text == '405: Method Not Allowed'


async def test_http_exception(app, aiohttp_client, loop):
    async def error(request):
        raise web.HTTPInternalServerError()

    app.router.add_get('/error', error)

    client = await aiohttp_client(app)
    resp = await client.get('/error')
    assert resp.status == 500
    text = await resp.text()
    assert text == '500: Internal Server Error'


async def test_no_route(app, aiohttp_client, loop):
    client = await aiohttp_client(app)
    headers = {'user-agent': 'GitHub-Hookshot/asef3'}
    resp = await client.post('/hooks/github/', headers=headers, json={})
    assert resp.status == 501
    text = await resp.text()
    assert text == '501: GitHub route undefined'


async def test_no_user_agent(app, aiohttp_client, loop):
    client = await aiohttp_client(app)
    headers = {'X-GitHub-Event': 'issues'}
    data = {'action': 'created'}
    response = await client.post('/hooks/github/', headers=headers, json=data)
    assert response.status == 406
    text = await response.text()
    assert text == '406: User agent looks incorrect'


async def test_non_json(app, aiohttp_client, loop):
    client = await aiohttp_client(app)
    headers = {'user-agent': 'GitHub-Hookshot/asef3', 'X-GitHub-Event': 'issues'}
    response = await client.post('/hooks/github/', headers=headers, data=b'bytes')
    assert response.status == 415
    text = await response.text()
    assert text == '415: Not a JSON payload'
