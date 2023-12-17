from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

from models.conversation import Conversation, Message

class MongoService:

    def create_conversation(self, db: MongoClient, conversation: Conversation) -> str:
        conversation_json = jsonable_encoder(conversation)
        new_conversation = db["conversations"].insert_one(conversation_json)
        return new_conversation.inserted_id
    
    def get_conversation_by_id(self, db: MongoClient, conversation_id: str) -> Conversation:
        conversation: Conversation = db["conversations"].find_one({"_id": conversation_id})
        return conversation
    
    def append_message_to_conversation(self, db: MongoClient, message: Message, conversation_id: str):
        filter_criteria = {"_id": conversation_id}
        update_query = {"$push": {"messages": jsonable_encoder(message)}}
        db["conversations"].update_one(filter_criteria, update_query)

