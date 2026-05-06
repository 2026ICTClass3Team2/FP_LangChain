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


class VerifyAnswerRequest(BaseModel):
    question_title: str
    question_body: str
    comment_body: str


class VerifyAnswerResponse(BaseModel):
    is_answer: bool


@router.post("/event/generate", response_model=EventQuestionsResponse)
async def generate_event_questions():
    questions = event_svc.generate_event_questions()
    return EventQuestionsResponse(
        questions=[EventQuestion(**q) for q in questions]
    )


@router.post("/event/verify", response_model=VerifyAnswerResponse)
async def verify_event_answer(req: VerifyAnswerRequest):
    is_answer = event_svc.verify_answer(req.question_title, req.question_body, req.comment_body)
    return VerifyAnswerResponse(is_answer=is_answer)
