from fastapi import APIRouter
from app.services.review_service import ReviewService
from app.models.schemas import QnA

router = APIRouter()
review_svc = ReviewService()

@router.post("/qna/assess")
def assess_qna(question: str):
    assessment = review_svc.assess_qna(question)
    qna = QnA(
        id=f"qna_{len(question)}",
        question=question,
        difficulty=assessment["difficulty"],
        points=assessment["points"]
    )
    return qna