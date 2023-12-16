from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.requests import Request
from contextlib import asynccontextmanager
from dotenv import dotenv_values
from pymongo import MongoClient
from bson import ObjectId
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
    object_id = ObjectId("657e09615252cb4b2b20241f")
    person = request.app.database["collection"].find_one({"_id": object_id})
    return str(person["category"])