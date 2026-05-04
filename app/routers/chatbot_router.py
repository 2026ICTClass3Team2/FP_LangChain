from fastapi import APIRouter
from app.services.chatbot_service import ChatbotService
from typing import List, Optional
from pydantic import BaseModel

class ReviewRequest(BaseModel):
    code: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[str]] = []

router = APIRouter()
chatbot_svc = ChatbotService()

@router.post("/api/chatbot/review")
def review_code(req: ReviewRequest):
    review = chatbot_svc.review_code(req.code)
    return {"review": review}

@router.post("/api/chatbot/chat")
def chat(req: ChatRequest):
    response = chatbot_svc.chat(req.message, req.history)
    return {"response": response}
