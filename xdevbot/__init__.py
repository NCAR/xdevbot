from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount('/static', StaticFiles(directory='xdevbot/static'), name='static')

templates = Jinja2Templates(directory='xdevbot/templates')


@app.get('/')
async def root(request: Request):
    params = {'request': request, 'title': 'Xdevbot', 'watching': None}
    return templates.TemplateResponse('home.html.j2', params)
