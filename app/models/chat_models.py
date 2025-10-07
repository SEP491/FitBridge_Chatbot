# app/models/chat_models.py - Chat-related Pydantic models

from typing import List, Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt: str
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    conversation_history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    promptResponse: str
    gyms: Optional[List[dict]] = None
    conversation_history: Optional[List[dict]] = []