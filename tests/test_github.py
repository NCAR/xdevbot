from fastapi import status
from fastapi.testclient import TestClient

from xdevbot.initialization import init_app


def test_no_route():
    app = init_app()
    client = TestClient(app)

    headers = {'user-agent': 'GitHub-Hookshot/asef3'}

    response = client.post('/', json={}, headers=headers)
    assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED


def test_issues_created():
    app = init_app()
    client = TestClient(app)

    headers = {'user-agent': 'GitHub-Hookshot/asef3', 'X-GitHub-Event': 'issues'}
    data = {'action': 'created'}

    response = client.post('/', json=data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
