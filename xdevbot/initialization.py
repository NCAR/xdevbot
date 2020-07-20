from fastapi import FastAPI

from xdevbot.views import init_views


def init_app():
    app = FastAPI()

    init_views(app)

    return app
