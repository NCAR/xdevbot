from motor.motor_asyncio import AsyncIOMotorDatabase

from ..cli import DEFAULT_CONFIG, init_app


async def test_database(aiohttp_client, mockdbserver, loop):
    config = DEFAULT_CONFIG.copy()
    config['mongouri'] = mockdbserver.uri
    app = await init_app(config=config)
    await aiohttp_client(app)
    db = app['db']
    assert isinstance(db, AsyncIOMotorDatabase)
