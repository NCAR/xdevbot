import os
from unittest import mock

import pytest
from aiohttp import streams, web
from aiohttp.test_utils import make_mocked_request

from xdevbot import github

NEW_COLUMN_ID = 10144279
OLD_COLUMN_ID = 9388249

PAYLOAD = b'{ "action": "opened", "content": { "body": "something" } }'

TOKEN = os.environ.get('XDEVBOT_TOKEN', None)


async def test_project_card_lifetime():
    note = 'https://github.com/NCAR/xdevbot-testing/issues/5'
    async with github.ProjectClientSession(token=TOKEN) as session:
        response = await session.create_project_card(note=note, column_id=NEW_COLUMN_ID)
        assert response.status == 201
        new_card = await response.json()

        response = await session.list_project_cards(column_id=NEW_COLUMN_ID)
        assert response.status == 200
        new_cards = await response.json()
        new_card_found = False
        for card in new_cards:
            if card['id'] == new_card['id']:
                new_card_found = True
        assert new_card_found

        response = await session.update_project_card(card_id=new_card['id'], archived=True)
        assert response.status == 200
        card = await response.json()
        assert card['archived']

        response = await session.update_project_card(card_id=new_card['id'], archived=False)
        assert response.status == 200
        card = await response.json()
        assert not card['archived']

        response = await session.get_project_card(card_id=new_card['id'])
        assert response.status == 200
        card = await response.json()
        assert card['id'] == new_card['id']
        assert card['note'] == new_card['note']

        response = await session.move_project_card(card_id=new_card['id'], column_id=OLD_COLUMN_ID)
        assert response.status == 201

        response = await session.delete_project_card(card_id=new_card['id'])
        assert response.status == 204


@pytest.mark.skipif(TOKEN is None, reason='requires a valid GitHub token')
async def test_graphql_query():
    query = '{repository(name: \"xdev\", owner: \"NCAR\") { url }}'
    actual = await github.graphql_query(query, token=TOKEN)
    expected = {'data': {'repository': {'url': 'https://github.com/NCAR/xdev'}}}
    assert actual == expected


async def test_graphql_query_failure():
    query = '{repository(name: \"xdev\", owner: \"NCAR\") { url }}'
    with pytest.raises(RuntimeError):
        await github.graphql_query(query, token='asdf')


def test_event_type():
    event = github.EventType(a=1, b=2)
    assert event.a == 1
    assert event.b == 2


async def test_issues_event(loop):
    headers = {
        'User-Agent': 'GitHub-Hookshot/abcde',
        'Content-Type': 'application/json',
        'X-GitHub-Event': 'issues',
        'X-GitHub-Delivery': 'askfjbcalskeuhfaw3r',
        'X-Hub-Signature': 'q3r5awfeaea',
    }
    protocol = mock.Mock(_reading_paused=False)
    payload = streams.StreamReader(protocol=protocol, loop=loop)
    payload.feed_data(PAYLOAD)
    payload.feed_eof()
    webhook_request = make_mocked_request('POST', '/', headers=headers, payload=payload)

    event = await github.Event(webhook_request)
    assert isinstance(event, github.EventType)
    assert event.app
    assert event.kind == 'issues'
    assert event.element == 'issue'
    assert event.action == 'opened'


async def test_pull_event(loop):
    headers = {
        'User-Agent': 'GitHub-Hookshot/abcde',
        'Content-Type': 'application/json',
        'X-GitHub-Event': 'pull_request',
        'X-GitHub-Delivery': 'askfjbcalskeuhfaw3r',
        'X-Hub-Signature': 'q3r5awfeaea',
    }
    protocol = mock.Mock(_reading_paused=False)
    payload = streams.StreamReader(protocol=protocol, loop=loop)
    payload.feed_data(PAYLOAD)
    payload.feed_eof()
    webhook_request = make_mocked_request('POST', '/', headers=headers, payload=payload)

    event = await github.Event(webhook_request)
    assert isinstance(event, github.EventType)
    assert event.app
    assert event.kind == 'pull_request'
    assert event.element == 'pull_request'
    assert event.action == 'opened'


async def test_route():
    @github.route('a', 'b')
    async def handler(request):
        return web.Response(text='OK')

    event = github.EventType(kind='a', action='b')
    assert github.router(event)

    event = github.EventType(kind='a', action='x')
    assert github.router(event)
