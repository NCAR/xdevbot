from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount('/static', StaticFiles(directory='xdevbot/static'), name='static')

templates = Jinja2Templates(directory='xdevbot/templates')


@app.middleware('http')
async def http_exception_handler(request: Request, call_next):
    response = await call_next(request)
    if response.status_code >= 400 and response.status_code < 500:
        return templates.TemplateResponse('404.html.j2', {'request': request})
    elif response.status_code >= 500:
        return templates.TemplateResponse('500.html.j2', {'request': request})
    return response


@app.get('/')
async def root(request: Request):
    params = {'request': request, 'title': 'Xdevbot', 'watching': None}
    return templates.TemplateResponse('home.html.j2', params)
