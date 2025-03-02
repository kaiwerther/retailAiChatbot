# api/chat.py
from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from core.database import get_checkpointer
from core.chatbot import create_chatbot_workflow
from models.conversation import Conversation, Message
from langchain_core.messages.ai import AIMessage
from core.app_state import workflow_app  # Import the global workflow_app

router = APIRouter()

# In-memory store for conversations
# Structure: { user_id: { conversation_id: Conversation, ... } }
conversations_db = {}

class ChatRequest(BaseModel):
    user_id: str
    conversation_id: Optional[str] = None  # If not provided, a new conversation is created.
    message: str
    language: str

class ChatResponse(BaseModel):
    conversation_id: str
    user_message: str
    ai_response: str
    messages: list[Message]

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):

    # Configuration: using conversation_id as thread_id, and passing user_id.
    config = {"configurable": {"thread_id": "randomt", "user_id": "user_id"}}

    ai_response = ""
    for chunk, metadata in workflow_app.stream(
        {"messages": request.message, "language": request.language},
        config,
        stream_mode="messages",
    ):
        # Here we assume chunk is a dict that contains the key "content".
        if isinstance(chunk, AIMessage):  # Filter to just model responses
            print(chunk.content, end="")
            ai_response = ai_response + chunk.content

    # Append the AI response to the conversation.

    return ai_response
