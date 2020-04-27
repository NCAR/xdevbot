import aiohttp_jinja2


@aiohttp_jinja2.template('index.html.j2')
async def index(request):
    return {}
