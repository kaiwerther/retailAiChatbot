# models/conversation.py
from typing import List
from pydantic import BaseModel

# message used for llm communication
class Message(BaseModel):
    role: str
    content: str

class Thread(BaseModel):
    thread_id: str
    user_id: str
    messages: List[Message]