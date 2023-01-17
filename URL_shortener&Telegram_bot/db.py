import os
import motor.motor_asyncio


async def setup_db():
    username = os.environ.get('DB_USERNAME')
    password = os.environ.get('DB_PASSWORD')
    host = os.environ.get('DB_HOST')
    port = os.environ.get('DB_PORT')
    client = motor.motor_asyncio.AsyncIOMotorClient(f"mongodb://{username}:{password}@{host}:{port}")
    db = client['async_db']
    return db
