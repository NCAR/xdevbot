import pandas as pd

from xdevbot.utils import refs_from_note


def build_config_frame(config: dict) -> pd.DataFrame:
    data = {'project_url': [], 'repo': []}
    for name in config:
        url = config[name]['url']
        repos = config[name]['repos']
        if repos:
            for repo in config[name]['repos']:
                data['project_url'].append(url)
                data['repo'].append(repo)
    return pd.DataFrame(data=data)


def build_cards_frame(projects: dict) -> pd.DataFrame:
    columns = build_columns_frame(projects)
    data = {
        'card_id': [],
        'ref': [],
        'content_id': [],
        'content_type': [],
        'content_state': [],
        'creator': [],
        'column_id': [],
        'column_name': [],
        'project_url': [],
        'new_column_id': [],
        'easy_column_id': [],
        'low_priority_column_id': [],
        'high_priority_column_id': [],
        'in_progress_column_id': [],
        'stalled_column_id': [],
        'done_column_id': [],
    }
    for project in projects['data']['repository']['projects']['nodes']:
        url = project['url']
        for column in project['columns']['nodes']:
            column_id = column['databaseId']
            column_name = column['name']
            for card in column['cards']['nodes']:
                card_id = card['databaseId']
                creator = card['creator']['login']

                skip_card = True
                ref = None
                content_id = None
                content_type = None
                content_state = None
                if card['content'] is not None:
                    skip_card = False
                    content_id = card['content']['databaseId']
                    content_type = card['content']['type']
                    content_state = card['content']['state']
                elif card['note'] is not None:
                    refs = refs_from_note(card['note'])
                    if len(refs) == 1:
                        skip_card = False
                        ref = refs[0]

                if skip_card:
                    continue

                data['card_id'].append(card_id)
                data['ref'].append(ref)
                data['content_id'].append(content_id)
                data['content_type'].append(content_type)
                data['content_state'].append(content_state)
                data['creator'].append(creator)
                data['column_id'].append(column_id)
                data['column_name'].append(column_name)
                data['project_url'].append(url)

                df = columns[columns['project_url'] == url]
                new_column_id = int(df[df['column_name'] == 'New']['column_id'])
                data['new_column_id'].append(new_column_id)
                easy_column_id = int(df[df['column_name'] == 'Easy']['column_id'])
                data['easy_column_id'].append(easy_column_id)
                low_priority_column_id = int(df[df['column_name'] == 'Low Priority']['column_id'])
                data['low_priority_column_id'].append(low_priority_column_id)
                high_priority_column_id = int(df[df['column_name'] == 'High Priority']['column_id'])
                data['high_priority_column_id'].append(high_priority_column_id)
                in_progress_column_id = int(df[df['column_name'] == 'In Progress']['column_id'])
                data['in_progress_column_id'].append(in_progress_column_id)
                stalled_column_id = int(df[df['column_name'] == 'Stalled']['column_id'])
                data['stalled_column_id'].append(stalled_column_id)
                done_column_id = int(df[df['column_name'] == 'Done']['column_id'])
                data['done_column_id'].append(done_column_id)
    return pd.DataFrame(data=data)


def build_columns_frame(projects: dict) -> pd.DataFrame:
    data = {'project_url': [], 'column_name': [], 'column_id': []}
    for project in projects['data']['repository']['projects']['nodes']:
        project_url = project['url']
        for column in project['columns']['nodes']:
            column_name = column['name']
            column_id = column['databaseId']

            data['project_url'].append(project_url)
            data['column_name'].append(column_name)
            data['column_id'].append(column_id)
    return pd.DataFrame(data=data)
