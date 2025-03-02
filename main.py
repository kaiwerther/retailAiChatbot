# main.py

import os
import logging
from fastapi import FastAPI

def create_app() -> FastAPI:
    # Determine debug mode from environment variable
    debug_mode = os.environ.get("DEBUG", "False").lower() in ["true", "1"]
    
    # Create the FastAPI app instance with some metadata
    app = FastAPI(
        title="Chat API",
        debug=debug_mode,
        description="An example chat api for personal learning purpose."
    )
    
    # Include routers from your API modules
    from api import chat
    app.include_router(chat.router, prefix="/api", tags=["chat"])
    
    return app

# Create the app instance using our factory function
app = create_app()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Retrieve configuration from environment variables
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    
    import uvicorn
    uvicorn.run("main:app", host=host, port=port)
