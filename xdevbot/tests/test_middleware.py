from bs4 import BeautifulSoup
from fastapi import Request
from fastapi.testclient import TestClient

from xdevbot import app


def test_404():
    client = TestClient(app)

    response = client.get('/*&!@#$%')
    assert response.status_code == 200

    html_doc = response.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    assert soup.title.string == '404 Page Not Found'


def test_405():
    client = TestClient(app)

    response = client.post('/', data={'message': 'ERROR!'})
    assert response.status_code == 200

    html_doc = response.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    assert soup.title.string == '404 Page Not Found'


def test_500():
    @app.get('/error')
    async def error(request: Request):
        raise RuntimeError('error!')

    client = TestClient(app)

    response = client.get('/error')
    assert response.status_code == 200

    html_doc = response.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    assert soup.title.string == '500 Internal Server Error'
