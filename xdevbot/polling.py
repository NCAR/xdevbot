import asyncio
import logging

import pandas as pd

from xdevbot import github, projects, queries, utils

logger = logging.getLogger('xdevbot')


async def polling(period=120, token=None):
    while True:
        logger.info(f'Polling GitHub API (every {period} seconds)')
        await update_nonbot_cards(token=token)
        await asyncio.sleep(period)


async def update_nonbot_cards(token=None):
    card_data = await github.graphql_query(queries.GET_ALL_CARDS, token=token)
    columns = projects.build_columns_frame(card_data)
    cards = projects.build_cards_frame(card_data)
    nonbot_cards = cards[cards['creator'] != 'xdev-bot']
    logger.debug(f'Found {len(nonbot_cards)} non-bot cards on project boards')
    num_cards_moved = 0
    num_failures = 0
    for _, card in nonbot_cards.iterrows():
        card_id = card['card_id']
        project_url = card['project_url']
        column_id = card['column_id']

        df = columns[columns['project_url'] == project_url]
        column_name = df[df['column_id'] == column_id]['column_name'].item()

        ref = card['ref']
        content_id = card['content_id']

        if not pd.isna(content_id):
            state = card['content_state'].lower()
        elif not pd.isna(ref):
            owner, repo, number = utils.split_issue_ref(ref)
            async with github.IssueClientSession(token=token) as session:
                response = await session.get_issue(owner=owner, repo=repo, number=number)
                if response.status != 200:
                    logger.warning(
                        f'Failed to retrieve state of reference: {owner}/{repo}#{number}'
                    )
                    continue
            issue = await response.json()
            state = issue['state']
        else:
            logger.warning(f'Non-bot card {card_id} has no content_id or reference. Skipping.')
            continue

        if state == 'open' and column_name == 'Done':
            logger.debug(f'Non-bot card {card_id} is open but was found in the "Done" column')
            column_id = card['inprog_column_id']
        elif state != 'open' and column_name != 'Done':
            logger.debug(f'Non-bot card {card_id} is closed but wasn\'t found in the "Done" column')
            column_id = card['done_column_id']
        else:
            logger.debug(f'Non-bot card {card_id} appears to be in a consistent column')
            column_id = None

        if column_id:
            async with github.ProjectClientSession(token=token) as session:
                logger.debug(f'Moving non-bot card {card_id} to column {column_id}')
                response = await session.move_project_card(card_id=card_id, column_id=column_id)
                if response.status == 201:
                    num_cards_moved += 1
                else:
                    num_failures += 1
                    logger.warning(f'Failed to move non-bot card [{response.status}]')

    if num_cards_moved > 0:
        logger.info(
            f'Updated {num_cards_moved} non-bot cards on project boards ({num_failures} failures)'
        )
