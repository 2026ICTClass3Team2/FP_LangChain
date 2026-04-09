from fastapi import APIRouter
from app.services.chatbot_service import ChatbotService
from typing import List

router = APIRouter()
chatbot_svc = ChatbotService()

@router.post("/chatbot/review")
def review_code(code: str):
    review = chatbot_svc.review_code(code)
    return {"review": review}

@router.post("/chatbot/chat")
def chat(message: str, history: List[str] = []):
    response = chatbot_svc.chat(message, history)
    return {"response": response}