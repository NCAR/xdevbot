import click
from aiohttp import web

from .application import init_app

NAME = __package__


@click.command()
@click.option('--host', default=None, type=str, help='Server IP address')
@click.option('--port', default=None, type=int, help='Server port number')
def cli(host, port):
    web.run_app(init_app(), host=host, port=port)
