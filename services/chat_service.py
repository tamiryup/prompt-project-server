from typing import Generator
from openai import OpenAI
from pymongo import MongoClient

from services.mongo_service import MongoService
from models.conversation import Message, Conversation

client = OpenAI()

class ChatService:

    def __init__(self, mongo_service: MongoService):
        self.mongo_service: MongoService = mongo_service

    def new_conversation(self, db: MongoClient) -> str:
        message: Message = Message(role="system", content="You are a helpful assistant")
        conversation: Conversation = Conversation(messages=[message])
        new_conversation_id: str = self.mongo_service.create_conversation(db, conversation)
        return new_conversation_id