import pytest

from xdevbot.cli import init_app


@pytest.fixture
async def app():
    return await init_app()


async def test_issues_created(app, aiohttp_client, loop):
    client = await aiohttp_client(app)
    headers = {'user-agent': 'GitHub-Hookshot/asef3', 'X-GitHub-Event': 'issues'}
    data = {'action': 'created'}
    response = await client.post('/hooks/github/', headers=headers, json=data)
    assert response.status == 200
    text = await response.text()
    assert text == 'Thanks!'
