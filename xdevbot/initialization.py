from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from xdevbot.middleware import init_middleware
from xdevbot.views import init_views


def init_app():
    app = FastAPI()
    app.mount('/static', StaticFiles(directory='xdevbot/static'), name='static')

    templates = Jinja2Templates(directory='xdevbot/templates')

    init_middleware(app, templates)
    init_views(app, templates)

    return app
