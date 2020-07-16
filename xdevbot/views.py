from fastapi import Request
from fastapi.templating import Jinja2Templates


def init_views(app, templates: Jinja2Templates):
    @app.get('/')
    async def root(request: Request):
        params = {'request': request, 'title': 'Xdevbot', 'watching': None}
        return templates.TemplateResponse('home.html.j2', params)
