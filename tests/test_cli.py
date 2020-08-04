import pytest

from xdevbot.cli import NAME, cli

DEFAULT_CONFIG = {'host': None, 'port': None, 'token': None}


@pytest.fixture
def cli_env(monkeypatch):
    monkeypatch.setenv(f'{NAME.upper()}_HOST', 'http://127.0.0.1')
    monkeypatch.setenv(f'{NAME.upper()}_PORT', '6789')
    monkeypatch.setenv(f'{NAME.upper()}_TOKEN', 'sometoken')


def test_cli_defaults():
    ctx = cli.make_context(cli.name, args=[], auto_envvar_prefix=NAME)
    assert ctx.params == DEFAULT_CONFIG


def test_cli_host():
    params = DEFAULT_CONFIG.copy()
    params['host'] = 'http://localhost'
    ctx = cli.make_context(cli.name, args=['--host', params['host']], auto_envvar_prefix=NAME)
    assert ctx.params == params


def test_cli_port():
    params = DEFAULT_CONFIG.copy()
    params['port'] = 4567
    ctx = cli.make_context(cli.name, args=['--port', str(params['port'])], auto_envvar_prefix=NAME)
    assert ctx.params == params


def test_cli_token():
    params = DEFAULT_CONFIG.copy()
    params['token'] = 'xtokenx'
    ctx = cli.make_context(
        cli.name, args=['--token', str(params['token'])], auto_envvar_prefix=NAME
    )
    assert ctx.params == params


def test_cli_env(cli_env):
    params = DEFAULT_CONFIG.copy()
    params['host'] = 'http://127.0.0.1'
    params['port'] = 6789
    params['token'] = 'sometoken'
    ctx = cli.make_context(cli.name, args=[], auto_envvar_prefix=NAME)
    assert ctx.params == params


def test_cli_env_overridden(cli_env):
    params = DEFAULT_CONFIG.copy()
    params['host'] = 'http://127.0.0.1'
    params['port'] = 9999
    params['token'] = 'sometoken'
    ctx = cli.make_context(cli.name, args=['--port', str(params['port'])], auto_envvar_prefix=NAME)
    assert ctx.params == params
