import pathlib

from .views import ghmain, ghwatch, home

PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app):
    app.router.add_get('/', home)
    app.router.add_post('/ghmain', ghmain)
    app.router.add_post('/ghwatch', ghwatch)
    setup_static_routes(app)


def setup_static_routes(app):
    app.router.add_static('/static/', path=PROJECT_ROOT / 'static', name='static')
