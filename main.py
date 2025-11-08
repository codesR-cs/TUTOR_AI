from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
import asyncio

from backend.router_ai import route_and_respond
from backend.utils import sanitize_input, chat_memory

load_dotenv()

app = FastAPI(title="TutorAI+")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session memory storage
sessions = {}

class ChatRequest(BaseModel):
    message: str
    mode: str = "auto"
    session_id: str = "default"

class ResetRequest(BaseModel):
    session_id: str = "default"

@app.post("/api/respond")
async def respond(request: ChatRequest):
    try:
        # Sanitize input
        message = sanitize_input(request.message)
        
        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get or create session memory
        if request.session_id not in sessions:
            sessions[request.session_id] = []
        
        session_memory = sessions[request.session_id]
        
        # Route and respond
        response = await route_and_respond(message, request.mode, session_memory)
        
        # Update memory (keep last 7 exchanges = 14 messages)
        session_memory.append({"role": "user", "content": message})
        session_memory.append({"role": "assistant", "content": response.get("main_content", "")})
        
        if len(session_memory) > 14:  # 7 exchanges = 14 messages
            session_memory[:] = session_memory[-14:]
        
        sessions[request.session_id] = session_memory
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset")
async def reset_chat(request: ResetRequest):
    try:
        if request.session_id in sessions:
            sessions[request.session_id] = []
        return {"status": "success", "message": "Chat memory cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve frontend
app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")

@app.get("/")
async def read_root():
    return FileResponse("frontend/index.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "TutorAI+"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)