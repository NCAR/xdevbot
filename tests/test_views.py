import pytest
from async_asgi_testclient import TestClient  # noqa
from bs4 import BeautifulSoup  # noqa

from xdevbot.initialization import init_app


@pytest.mark.asyncio
async def test_index():
    app = init_app()

    async with TestClient(app) as client:
        response = await client.get('/')
        assert response.status_code == 200
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        assert soup.title.string == 'Xdevbot'
