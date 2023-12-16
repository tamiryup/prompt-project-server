from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder

from models.conversation import Conversation

class MongoService:

    def create_conversation(self, db: MongoClient, conversation: Conversation) -> str:
        conversation_json = jsonable_encoder(conversation)
        new_conversation = db["conversations"].insert_one(conversation_json)
        return new_conversation.inserted_id
