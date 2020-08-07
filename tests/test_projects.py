import json

import pandas as pd
import yaml

from xdevbot import projects


def test_build_config_frame():
    with open('tests/data/config.yaml') as f:
        config_data = yaml.safe_load(f)
    actual = projects.build_config_frame(config_data)
    expected = pd.read_csv('tests/data/config.csv')
    pd.testing.assert_frame_equal(actual, expected)


def test_build_cards_frame():
    with open('tests/data/cards.json') as f:
        cards_data = json.load(f)
    actual = projects.build_cards_frame(cards_data)
    expected = pd.read_csv('tests/data/cards.csv', index_col=0)
    pd.testing.assert_frame_equal(actual, expected)


_data = {
    'project_url': (
        ['https://github.com/owner/repo/projects/1'] * 3
        + ['https://github.com/owner/repo/projects/2'] * 3
    ),
    'column_name': ['New', 'Done', 'In Progress'] * 2,
    'column_id': [11, 12, 13, 21, 22, 23],
}
COLUMNS = pd.DataFrame(data=_data)


def test_build_columns_frame_from_cards():
    with open('tests/data/cards.json') as f:
        cards_data = json.load(f)
    actual = projects.build_columns_frame(cards_data)
    pd.testing.assert_frame_equal(actual, COLUMNS)


def test_build_columns_frame_from_columns():
    with open('tests/data/columns.json') as f:
        columns_data = json.load(f)
    actual = projects.build_columns_frame(columns_data)
    pd.testing.assert_frame_equal(actual, COLUMNS)
