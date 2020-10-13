#!/usr/bin/env python

import asyncio
import os

from xdevbot import github, projects, routes, utils

from .query import GET_ALL_CARDS

BACKLOG_URL = 'https://github.com/NCAR/xdev/projects/1'

BACKLOG_COLUMN_MAP = {
    'Backlog': 'New',
    'Move, Close or Don\'t Watch?': 'New',
    'Easy to Do': 'Easy',
    'High Priority (~3 Issues/Person)': 'High Priority',
    'In Progress': 'In Progress',
    'Waiting': 'Stalled',
    'Done': 'Done',
}


async def main():
    token = os.environ.get('XDEVBOT_TOKEN', None)

    cfg_data = await utils.read_remote_yaml(routes.CONFIG_URL)
    cfg_df = projects.build_config_frame(cfg_data)

    all_card_data = await github.graphql_query(GET_ALL_CARDS, token=token)
    all_cards_df = projects.build_cards_frame(all_card_data)
    columns_df = projects.build_columns_frame(all_card_data)

    new_cards_df = all_cards_df[all_cards_df['project_url'].isin(cfg_df['project_url'])]
    old_cards_df = all_cards_df[all_cards_df['project_url'] == BACKLOG_URL]

    unwatched = set()
    existing = set()
    missing = set()
    nonbot = set()

    for _, old_card in old_cards_df.iterrows():
        ref = old_card['ref']
        new_cards = new_cards_df[new_cards_df['ref'] == ref]
        if len(new_cards) > 0:
            existing.add(ref)
            continue

        creator = old_card['creator']
        if creator != 'xdev-bot':
            nonbot.add(ref)
            continue

        org, user, _ = utils.split_issue_ref(ref)
        repo = f'{org}/{user}'
        project_urls = cfg_df[cfg_df['repo'] == repo]['project_url'].to_list()
        if len(project_urls) == 0:
            unwatched.add(repo)
            continue

        missing.add(ref)
        print()
        print(f'--- Need to copy card: {ref}')

        old_column = old_card['column_name']
        new_column = BACKLOG_COLUMN_MAP[old_column]
        print(f'    From column "{old_column}"')

        async with github.ProjectClientSession(token=token) as session:
            for project_url in project_urls:
                df = columns_df[columns_df['project_url'] == project_url]
                column_id = int(df[df['column_name'] == new_column]['column_id'])
                print(f'    To project {project_url} column "{new_column}" [id: {column_id}]')

                response = await session.create_project_card(note=ref, column_id=column_id)
                if response.status != 201:
                    print(f'    *** Failed to transfer card! [{response.status}]')

    if unwatched:
        print()
        print('=== Unwatched Repositories:')
        for repo in sorted(unwatched):
            print(f'    - {repo}')

    if nonbot:
        print()
        print('=== Non-bot cards that were skipped:')
        for ref in sorted(nonbot):
            print(f'    - {ref}')

    if existing:
        print()
        print(f'Found {len(existing)} existing cards that were skipped.')

    if missing:
        print()
        print(f'Will copy {len(missing)} cards to new boards.')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
