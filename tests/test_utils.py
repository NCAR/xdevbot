import pytest
import yaml
from aiohttp import web

from xdevbot import utils


@pytest.fixture
def yaml_text():
    with open('tests/data/test.yaml') as f:
        text = f.read()
    return text


@pytest.fixture
async def yaml_server(yaml_text, aiohttp_server):
    async def yaml_handler(request):
        return web.Response(text=yaml_text)

    app = web.Application()
    app.router.add_get('/', yaml_handler)
    return await aiohttp_server(app, port=9876)


async def test_read_remote_yaml(yaml_text, yaml_server):
    data = await utils.read_remote_yaml('http://localhost:9876/')
    assert data == yaml.load(yaml_text)


async def test_read_remote_yaml_failure(yaml_text, yaml_server):
    with pytest.raises(RuntimeError):
        await utils.read_remote_yaml('http://localhost:9876/abcde', timeout=5)


def test_repo_fullname_from_url():
    repo = 'owner/repo'
    url = f'https://github.com/{repo}'
    assert utils.repo_fullname_from_url(url) == repo


def test_split_issue_ref():
    owner = 'owner'
    repo = 'repo'
    number = 5
    ref = f'https://github.com/{owner}/{repo}/pull/{number}'
    assert utils.split_issue_ref(ref) == (owner, repo, number)


def test_refs_from_note():
    ref1 = 'https://github.com/abc/xyz/issues/7'
    ref2 = 'http://github.com/abc/xyz/pull/49'
    note = f"""
here's a note it has
a url {ref1} in it
and another {ref2} and
then a bad url https://github/abc/xyz/pull/52
and another bad url https://github.com/abc/xyz/pull/xx
"""
    refs = utils.refs_from_note(note)
    assert set(refs) == set([ref1, ref2])


async def test_log_rate_limits():
    await utils.log_rate_limits(category=['core', 'graphql'])
    await utils.log_rate_limits(token='asfasef')
