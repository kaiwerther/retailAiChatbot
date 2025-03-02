# api/conversations.py
from fastapi import APIRouter, HTTPException
from typing import List
from models.conversation import Conversation, Message

router = APIRouter()

# Dummy in-memory store; in production, you would query your Postgres DB.
conversations_db = {}  # {user_id: [Conversation, ...]}

@router.get("/user/{user_id}", response_model=List[Conversation])
async def get_user_conversations(user_id: str):
    """
    Get all conversations for a given user.
    """
    return conversations_db.get(user_id, [])

@router.post("/", response_model=Conversation)
async def create_conversation(user_id: str, initial_message: Message):
    """
    Create a new conversation for a user with an initial message.
    """
    conversation_id = f"conv_{len(conversations_db.get(user_id, [])) + 1}"
    conversation = Conversation(conversation_id=conversation_id, user_id=user_id, messages=[initial_message])
    conversations_db.setdefault(user_id, []).append(conversation)
    return conversation
