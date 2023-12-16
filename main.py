from fastapi import FastAPI, Depends
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
import deps as deps
from services.chat_service import ChatService
from services.mongo_service import MongoService

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
def new_conversation(request: Request, chat_service: ChatService = Depends(deps.get_chat_service)):
    new_conversation_id = chat_service.new_conversation(request.app.database)
    return new_conversation_id