from fastapi import HTTPException, Request, status
from fastapi.testclient import TestClient

from xdevbot.initialization import init_app


def test_404():
    app = init_app()
    client = TestClient(app)

    response = client.get('/unknown')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data == {'detail': 'Not Found'}


def test_405():
    app = init_app()
    client = TestClient(app)

    response = client.get('/')
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_http_exception():
    app = init_app()

    @app.get('/error')
    async def error(request: Request):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    client = TestClient(app)
    response = client.get('/error')
    assert response.status_code == 500
