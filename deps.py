from fastapi import Depends

from services.mongo_service import MongoService
from services.chat_service import ChatService


def get_mongo_service() -> MongoService:
    return MongoService()

def get_chat_service(mongo_service: MongoService = Depends(get_mongo_service)) -> ChatService:
    return ChatService(mongo_service)
