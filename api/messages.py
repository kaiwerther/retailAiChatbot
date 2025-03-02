# api/messages.py
from fastapi import APIRouter, HTTPException
from models.conversation import Conversation, Message
from typing import List

router = APIRouter()

# Assume we have access to the same in-memory store (or ideally use a service layer that queries the database)
from api.conversations import conversations_db

@router.get("/{conversation_id}", response_model=List[Message])
async def get_messages(conversation_id: str, user_id: str):
    """
    Get all messages for a specific conversation.
    """
    user_convs = conversations_db.get(user_id, [])
    for conv in user_convs:
        if conv.conversation_id == conversation_id:
            return conv.messages
    raise HTTPException(status_code=404, detail="Conversation not found")

@router.post("/{conversation_id}", response_model=List[Message])
async def add_message(conversation_id: str, user_id: str, message: Message):
    """
    Add a new message to an existing conversation.
    """
    user_convs = conversations_db.get(user_id, [])
    for conv in user_convs:
        if conv.conversation_id == conversation_id:
            conv.messages.append(message)
            return conv.messages
    raise HTTPException(status_code=404, detail="Conversation not found")
