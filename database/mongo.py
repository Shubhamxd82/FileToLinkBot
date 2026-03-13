import motor.motor_asyncio
from config import Config

class MongoDB:
    _instance = None
    _client = None
    _db = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._client = motor.motor_asyncio.AsyncIOMotorClient(Config.MONGO_URI)
            cls._db = cls._client[Config.MONGO_DB_NAME]
        return cls._instance

    @classmethod
    def get_db(cls):
        if cls._db is None:
            cls.get_instance()
        return cls._db

    @classmethod
    def get_collection(cls, name):
        return cls.get_db()[name]

    @classmethod
    async def close(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
            cls._instance = None

    @classmethod
    async def ping(cls):
        try:
            await cls._client.admin.command('ping')
            return True
        except:
            return False

def get_db():
    return MongoDB.get_db()

def get_col(name):
    return MongoDB.get_collection(name)
