import os

import pytest

from xdevbot.github import ProjectClientSession

NEW_COLUMN_ID = 10144279
OLD_COLUMN_ID = 9388249


USERNAME = os.environ.get('GITHUB_TEST_USER', None)
TOKEN = os.environ.get('GITHUB_TEST_TOKEN', None)


@pytest.mark.asyncio
async def test_project_card_lifetime():
    note = 'https://github.com/NCAR/xdevbot-testing/issues/5'
    async with ProjectClientSession(username=USERNAME, token=TOKEN) as session:
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
