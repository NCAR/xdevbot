from ..cli import DEFAULT_CONFIG, NAME, cli


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


def test_cli_logging():
    params = DEFAULT_CONFIG.copy()
    params['logging'] = 'WARNING'
    ctx = cli.make_context(
        cli.name, args=['--logging', str(params['logging'])], auto_envvar_prefix=NAME
    )
    assert ctx.params == params


def test_cli_mongouri():
    params = DEFAULT_CONFIG.copy()
    params['mongouri'] = 'mongodb://test.mongodb.com'
    ctx = cli.make_context(
        cli.name, args=['--mongouri', params['mongouri']], auto_envvar_prefix=NAME
    )
    assert ctx.params == params


def test_cli_mongodb():
    params = DEFAULT_CONFIG.copy()
    params['mongodb'] = 'test'
    ctx = cli.make_context(cli.name, args=['--mongodb', params['mongodb']], auto_envvar_prefix=NAME)
    assert ctx.params == params


def test_cli_env(cli_env):
    params = DEFAULT_CONFIG.copy()
    params['host'] = 'http://127.0.0.1'
    params['port'] = 6789
    ctx = cli.make_context(cli.name, args=[], auto_envvar_prefix=NAME)
    assert ctx.params == params


def test_cli_env_overridden(cli_env):
    params = DEFAULT_CONFIG.copy()
    params['host'] = 'http://127.0.0.1'
    params['port'] = 9999
    ctx = cli.make_context(cli.name, args=['--port', str(params['port'])], auto_envvar_prefix=NAME)
    assert ctx.params == params


def test_cli_configfile(cli_configfile):
    params = DEFAULT_CONFIG.copy()
    params['host'] = 'http://0.0.0.0'
    params['port'] = 9999
    ctx = cli.make_context(cli.name, args=['--config', cli_configfile], auto_envvar_prefix=NAME)
    assert ctx.params == params


def test_cli_configfile_overridden(cli_configfile):
    params = DEFAULT_CONFIG.copy()
    params['host'] = 'http://0.0.0.0'
    params['port'] = 8888
    ctx = cli.make_context(
        cli.name,
        args=['--config', cli_configfile, '--port', str(params['port'])],
        auto_envvar_prefix=NAME,
    )
    assert ctx.params == params


def test_cli_env_configfile_overridden(cli_env, cli_configfile):
    params = DEFAULT_CONFIG.copy()
    params['host'] = 'http://127.0.0.1'
    params['port'] = 8888
    ctx = cli.make_context(
        cli.name,
        args=['--config', cli_configfile, '--port', str(params['port'])],
        auto_envvar_prefix=NAME,
    )
    assert ctx.params == params
