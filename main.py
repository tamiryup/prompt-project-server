from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.requests import Request
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager
from dotenv import dotenv_values
from pymongo import MongoClient
from bson import ObjectId
from models.conversation import Message, Conversation
from openai import OpenAI

import chat as chat

config = dotenv_values(".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print("Connected to the MongoDB database!")

    yield #shutdown
    app.mongodb_client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/conversation")
def conversation(message: str, conversation_id: str = None):
    return StreamingResponse(chat.send_message(message))

@app.get("/new-conversation", response_model=str)
def new_conversation(request: Request):
    message: Message = Message(role="system", content="You are a helpful assistant")
    conversation: Conversation = Conversation(messages=[message])
    conversation_json = jsonable_encoder(conversation)
    new_conversation = request.app.database["conversations"].insert_one(conversation_json)
    return new_conversation.inserted_id

    # object_id = ObjectId("657e09615252cb4b2b20241f")
    # person = request.app.database["collection"].find_one({"_id": object_id})
    # return str(person["category"])