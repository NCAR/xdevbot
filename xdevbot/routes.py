import pathlib

from .views import github, home

PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app):
    app.router.add_get('/', home)
    app.router.add_post('/github', github)
    setup_static_routes(app)


def setup_static_routes(app):
    app.router.add_static('/static/', path=PROJECT_ROOT / 'static', name='static')
