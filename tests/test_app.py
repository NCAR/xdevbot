import pytest
from fastapi import HTTPException, Request, status
from fastapi.testclient import TestClient

from xdevbot.application import init_app


@pytest.fixture
def app():
    return init_app()


def test_404(app):
    client = TestClient(app)
    response = client.get('/unknown')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data == {'detail': 'Not Found'}


def test_405(app):
    client = TestClient(app)
    response = client.get('/')
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    data = response.json()
    assert data == {'detail': 'Method Not Allowed'}


def test_http_exception(app):
    @app.get('/error')
    async def error(request: Request):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    client = TestClient(app)
    response = client.get('/error')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    data = response.json()
    assert data == {'detail': 'Internal Server Error'}


def test_no_route(app):
    client = TestClient(app)
    headers = {'user-agent': 'GitHub-Hookshot/asef3'}
    response = client.post('/', headers=headers, json={})
    assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED
    data = response.json()
    assert data == {'detail': 'GitHub route undefined'}


def test_issues_created(app):
    client = TestClient(app)
    headers = {'user-agent': 'GitHub-Hookshot/asef3', 'X-GitHub-Event': 'issues'}
    data = {'action': 'created'}
    response = client.post('/', headers=headers, json=data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == {'detail': 'Thanks!'}


def test_no_user_agent(app):
    client = TestClient(app)
    headers = {'X-GitHub-Event': 'issues'}
    data = {'action': 'created'}
    response = client.post('/', headers=headers, json=data)
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    data = response.json()
    assert data == {'detail': 'User agent looks incorrect'}


def test_non_json(app):
    client = TestClient(app)
    headers = {'user-agent': 'GitHub-Hookshot/asef3', 'X-GitHub-Event': 'issues'}
    data = {'action': 'created'}
    response = client.post('/', headers=headers, data=b'bytes')
    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    data = response.json()
    assert data == {'detail': 'Unsupported media type'}
