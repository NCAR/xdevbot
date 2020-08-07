import asyncio
import logging

from xdevbot import github, projects, queries, utils

logger = logging.getLogger('gunicorn.error')


async def polling(period=120, token=None):
    while True:
        logger.info('Polling GitHub API')
        await update_nonbot_cards(token=token)
        await asyncio.sleep(period)


async def update_nonbot_cards(token=None):
    card_data = await github.graphql_query(queries.GET_ALL_CARDS, token=token)
    columns = projects.build_columns_frame(card_data)
    cards = projects.build_cards_frame(card_data)
    nonbot_cards = cards[cards['creator'] != 'xdev-bot']
    for _, card in nonbot_cards.iterrows():
        project_url = card['project_url']
        column_id = card['column_id']

        df = columns[columns['project_url'] == project_url]
        column_name = df[df['column_id'] == column_id]['column_name']

        ref = card['ref']
        owner, repo, number = utils.split_issue_ref(ref)
        async with github.IssueClientSession(token=token) as session:
            response = await session.get_issue(owner=owner, repo=repo, number=number)
        if response.status != 200:
            logger.warning(f'Failed to retrieve state of reference: {owner}/{repo}#{number}')
            continue
        issue = await response.json()
        state = issue['state']

        if state == 'open' and column_name == 'Done':
            column_id = card['inprog_column_id']
        elif state == 'closed' and column_name != 'Done':
            column_id = card['done_column_id']
        else:
            column_id = None

        if column_id:
            async with github.ProjectClientSession(token=token) as session:
                card_id = card['card_id']
                logger.debug(f'Moving non-bot card {card_id} to column {column_id}')
                await session.move_project_card(card_id=card_id, column_id=column_id)

    logger.info('Updated non-bot cards on project boards')
