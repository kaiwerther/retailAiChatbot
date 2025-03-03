# api/chat.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from models.thread import Thread, Message
from langchain_core.messages.ai import AIMessage
from core.app_state import workflow_app, checkpointer  # Import the global workflow_app

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    language: str

# TODO: With auth we can remove the /users/{user_id} from the path.
# because we can get the user_id from the token.

@router.get("/users/{user_id}/threads", response_model=List[Thread])
async def get_user_threads(user_id: str):
    """
    TODO: Get all threads for a given user.
    """
    return []

@router.put("/users/{user_id}/threads", response_model=Thread)
async def put_user_thread(user_id: str, request: ChatRequest):
    """
    TODO: Create new threads.
    """
    return []

@router.delete("/users/{user_id}/threads/{thread_id}", response_model=Thread)
async def delete_user_thread(user_id: str, thread_id: str, request: ChatRequest):
    """
    TODO: delete a threads.
    """

    return []


@router.get("/users/{user_id}/threads/{thread_id}", response_model=Thread)
async def get_user_thread(user_id: str, thread_id: str):
    """
    TODO: get a complete thread.
    """
    
    # TODO: This is not user specific but thread specific,
    # check if this is easily solvable
    # we might end up adding the user_id to the thread_id
    config = {"configurable": {"user_id": user_id, "thread_id": user_id + " " + thread_id }}
    cp_data = checkpointer.get(config)
    
    # Extract the messages from the checkpoint data
    messages = cp_data.get("channel_values", {}).get("messages", [])
    
    # Convert each message to our Message model
    converted_messages = []
    for msg in messages:
        # Determine the role based on the class name
        if msg.__class__.__name__ == "HumanMessage":
            role = "user"
        elif msg.__class__.__name__ == "AIMessage":
            role = "assistant"
        else:
            role = "unknown"
        
        converted_messages.append(Message(role=role, content=msg.content))
    
    return Thread(thread_id=thread_id, user_id=user_id, messages=converted_messages)

@router.put("/users/{user_id}/threads/{thread_id}/messages", response_model=str)
async def put_new_message(user_id: str, thread_id: str, request: ChatRequest):
    """
    TODO: Chat endpoint here.
    """
    # Config to identify the current conversation
    config = {"configurable": {"user_id": user_id, "thread_id": user_id + " " + thread_id }}

    ai_response = ""

    # TODO: Stream data to frontend instead of collecting it all at once.
    for chunk, metadata in workflow_app.stream(
        {"messages": request.message, "language": request.language},
        config,
        stream_mode="messages",
    ):
        ai_response = ai_response + chunk.content

    return ai_response