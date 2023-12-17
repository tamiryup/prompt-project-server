from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import dotenv_values
from pymongo import MongoClient
from bson import ObjectId
from models.conversation import Message, Conversation
from openai import OpenAI

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # You can replace ["*"] with the specific domains you want to allow
    allow_credentials=True,
    allow_methods=["*"],  # You can replace ["*"] with the specific HTTP methods you want to allow
    allow_headers=["*"],  # You can replace ["*"] with the specific HTTP headers you want to allow
)

@app.get("/conversation")
def conversation(request: Request, message: str, conversation_id: str, chat_service: ChatService = Depends(deps.get_chat_service)):
    if(chat_service.security_check(message)):
        raise HTTPException(status_code=400, detail="This type of prompt breaks our guidelines")
    if(chat_service.invalid_conversation_id(request.app.database, conversation_id)):
        raise HTTPException(status_code=400, detail="Invalid Conversation Id")

    return StreamingResponse(chat_service.send_message(request.app.database, message, conversation_id))

@app.get("/new-conversation", response_model=str)
def new_conversation(request: Request, chat_service: ChatService = Depends(deps.get_chat_service)):
    new_conversation_id = chat_service.new_conversation(db=request.app.database)
    return new_conversation_id