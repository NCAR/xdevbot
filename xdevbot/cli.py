import click
from aiohttp import web

from .app import init_app

NAME = __package__

LOGLEVELS = ['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOGCHOICES = click.Choice(LOGLEVELS, case_sensitive=False)


@click.command()
@click.option('--host', default=None, type=str, help='Server IP address')
@click.option('--port', default=None, type=int, help='Server port number')
@click.option('--token', default=None, type=str, help='GitHub authorization token')
@click.option('--loglevel', default='INFO', type=LOGCHOICES, help='Logging level')
def cli(host, port, token, loglevel):
    web.run_app(init_app(token=token, loglevel=loglevel), host=host, port=port)
