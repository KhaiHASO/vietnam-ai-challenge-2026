from motor.motor_asyncio import AsyncIOMotorCollection

from app.db.mongo import get_database


class MongoRepository:
    collection_name: str

    def __init__(self, collection_name: str) -> None:
        self.collection_name = collection_name

    @property
    def collection(self) -> AsyncIOMotorCollection:
        return get_database()[self.collection_name]
