# main.py
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from api import conversations, messages, chat



app = FastAPI()

app.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
