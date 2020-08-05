import click
from aiohttp import web

from .app import init_app

NAME = __package__


@click.command()
@click.option('--host', default=None, type=str, help='Server IP address')
@click.option('--port', default=None, type=int, help='Server port number')
@click.option('--token', default=None, type=str, help='GitHub authorization token')
def cli(host, port, token):
    web.run_app(init_app(token=token), host=host, port=port)
