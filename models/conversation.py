# models/conversation.py
from typing import List
from pydantic import BaseModel

class Message(BaseModel):
    sender: str  # e.g., "user" or "ai"
    content: str

class Conversation(BaseModel):
    conversation_id: str
    user_id: str
    messages: List[Message]