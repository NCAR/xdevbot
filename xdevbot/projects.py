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
        'creator': [],
        'column_id': [],
        'project_url': [],
        'new_column_id': [],
        'done_column_id': [],
        'inprog_column_id': [],
    }
    for project in projects['data']['repository']['projects']['nodes']:
        url = project['url']
        for column in project['columns']['nodes']:
            column_id = column['databaseId']
            for card in column['cards']['nodes']:
                card_id = card['databaseId']
                refs = refs_from_note(card['note'])
                creator = card['creator']['login']

                if len(refs) == 1:
                    data['card_id'].append(card_id)
                    data['ref'].append(refs[0])
                    data['creator'].append(creator)
                    data['column_id'].append(column_id)
                    data['project_url'].append(url)

                    df = columns[columns['project_url'] == url]
                    new_column_id = int(df[df['column_name'] == 'New']['column_id'])
                    data['new_column_id'].append(new_column_id)
                    done_column_id = int(df[df['column_name'] == 'Done']['column_id'])
                    data['done_column_id'].append(done_column_id)
                    inprog_column_id = int(df[df['column_name'] == 'In Progress']['column_id'])
                    data['inprog_column_id'].append(inprog_column_id)
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
