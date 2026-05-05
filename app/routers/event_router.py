import logging
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.event_service import EventQnaService

logger = logging.getLogger(__name__)
router = APIRouter()
event_svc = EventQnaService()


class EventQuestion(BaseModel):
    title: str
    body: str
    difficulty: str
    points: int


class EventQuestionsResponse(BaseModel):
    questions: list[EventQuestion]


@router.post("/event/generate", response_model=EventQuestionsResponse)
async def generate_event_questions():
    questions = event_svc.generate_event_questions()
    return EventQuestionsResponse(
        questions=[EventQuestion(**q) for q in questions]
    )
