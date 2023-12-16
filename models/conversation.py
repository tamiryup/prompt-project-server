from pydantic import BaseModel, Field
from typing import List
import uuid

class Message(BaseModel):

    role: str
    content: str


class Conversation(BaseModel):

    id:str = Field(default_factory=uuid.uuid4, alias="_id")
    messages: List[Message]
