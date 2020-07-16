from fastapi import Request
from fastapi.templating import Jinja2Templates


def init_middleware(app, templates: Jinja2Templates):
    @app.middleware('http')
    async def http_error_handler(request: Request, call_next):
        try:
            response = await call_next(request)
        except Exception:
            return templates.TemplateResponse('500.html.j2', {'request': request})

        if response.status_code >= 400 and response.status_code < 500:
            return templates.TemplateResponse('404.html.j2', {'request': request})
        elif response.status_code >= 500:
            return templates.TemplateResponse('500.html.j2', {'request': request})
        return response
