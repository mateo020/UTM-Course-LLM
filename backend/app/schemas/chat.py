from pydantic import BaseModel
from typing import Dict, Any, Optional

class ChatRequest(BaseModel):
    question: str
    chatHistory: list[str] | None = None
