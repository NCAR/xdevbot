import json

import pandas as pd
import yaml

from xdevbot import projects


def test_build_config_frame():
    with open('tests/data/config.yaml') as f:
        config_data = yaml.load(f)
    actual = projects.build_config_frame(config_data)
    expected = pd.read_csv('tests/data/config.csv')
    pd.testing.assert_frame_equal(actual, expected)


def test_build_cards_frame():
    with open('tests/data/cards.json') as f:
        cards_data = json.load(f)
    actual = projects.build_cards_frame(cards_data)
    expected = pd.read_csv('tests/data/cards.csv', index_col=0)
    pd.testing.assert_frame_equal(actual, expected)


COLUMNS = {
    'https://github.com/owner/repo/projects/1': {'New': 11, 'Done': 12, 'In Progress': 13},
    'https://github.com/owner/repo/projects/2': {'New': 21, 'Done': 22, 'In Progress': 23},
}


def test_build_columns_map_from_cards():
    with open('tests/data/cards.json') as f:
        cards_data = json.load(f)
    actual = projects.build_columns_map(cards_data)
    assert actual == COLUMNS


def test_build_columns_map_from_columns():
    with open('tests/data/columns.json') as f:
        columns_data = json.load(f)
    actual = projects.build_columns_map(columns_data)
    assert actual == COLUMNS
