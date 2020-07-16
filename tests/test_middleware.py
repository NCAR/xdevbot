import pytest
from async_asgi_testclient import TestClient  # noqa
from bs4 import BeautifulSoup  # noqa
from fastapi import Request, Response

from xdevbot.initialization import init_app


@pytest.mark.asyncio
async def test_404():
    app = init_app()

    async with TestClient(app) as client:
        response = await client.get('/*&!@#$%')
        assert response.status_code == 200
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        assert soup.title.string == '404 Page Not Found'


@pytest.mark.asyncio
async def test_405():
    app = init_app()

    async with TestClient(app) as client:
        response = await client.post('/', data={'message': 'ERROR!'})
        assert response.status_code == 200
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        assert soup.title.string == '404 Page Not Found'


@pytest.mark.asyncio
async def test_500_exception():
    app = init_app()

    @app.get('/error')
    async def error(request: Request):
        raise RuntimeError('error!')

    async with TestClient(app) as client:
        response = await client.get('/error')
        assert response.status_code == 200
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        assert soup.title.string == '500 Internal Server Error'


@pytest.mark.asyncio
async def test_500_status():
    app = init_app()

    @app.get('/error')
    async def error(request: Request):
        return Response(status_code=500)

    async with TestClient(app) as client:
        response = await client.get('/error')
        assert response.status_code == 200
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        assert soup.title.string == '500 Internal Server Error'
