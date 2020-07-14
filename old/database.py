import motor.motor_asyncio


async def connect_db(app):
    if app['config']['mongouri']:
        uri = app['config']['mongouri']
        client = motor.motor_asyncio.AsyncIOMotorClient(uri, io_loop=app.loop)
        db = client[app['config']['mongodb']]
    else:
        db = None
    app['db'] = db


async def disconnect_db(app):
    pass
