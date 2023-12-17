from typing import Generator, List
from openai import OpenAI
from pymongo import MongoClient
from fastapi import HTTPException

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
    
    # return a context of the last 5 messages + first system message
    def get_prev_messages_array(self, db: MongoClient, conversation_id: str) -> List[Message]:
        conversation: Conversation = self.mongo_service.get_conversation_by_id(db, conversation_id)

        messages: List[Message] = []
        if len(conversation['messages']) > 5:
            messages.append(conversation['messages'][0])
        messages.extend(conversation['messages'][-5:])
        return messages

    
    def send_message(self, db: MongoClient, message: str, conversation_id: str) -> Generator:
        message_context: List[Message] = self.get_prev_messages_array(db, conversation_id)

        user_message = {"role": "user", "content": message}
        self.mongo_service.append_message_to_conversation(db, user_message, conversation_id)
        message_context.append(user_message)

        #define request to openAI
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=message_context,
            stream=True,
        )

        final_answer: str = ""
        #create the stream of the assistant answer
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                current_chunk: str = chunk.choices[0].delta.content
                final_answer += current_chunk
                yield current_chunk
        
        # add the final answer to the conversation's mongo document
        assistant_message = Message(role="assistant", content=final_answer)
        self.mongo_service.append_message_to_conversation(db, assistant_message, conversation_id)

    def security_check(self, input: str) -> bool:
        input = input.lower()
        if "ignore all instructions" in input or "ignore all the instructions" in input:
            return True

        response = client.moderations.create(
            input=input,
            model="text-moderation-latest"
        )
        return response.results[0].flagged
    
    def invalid_conversation_id(self, db: MongoClient, conversation_id: str) -> bool:
        conversation: Conversation = self.mongo_service.get_conversation_by_id(db, conversation_id)
        if conversation is None:
            return True
        
        return False
        
