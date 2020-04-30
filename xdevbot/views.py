import aiohttp_jinja2


@aiohttp_jinja2.template('landing.html.j2')
async def landing(request):
    return {'title': 'Xdevbot'}


@aiohttp_jinja2.template('configure.html.j2')
async def configure(request):
    return {'title': 'Xdevbot'}
