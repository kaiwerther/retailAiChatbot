# core/app_state.py
from core.database import get_checkpointer
from core.chatbot import create_chatbot_workflow

# Create a single checkpointer and workflow_app that will be reused across API calls.
checkpointer = get_checkpointer()
workflow_app = create_chatbot_workflow(checkpointer)
