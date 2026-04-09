from fastapi import APIRouter
from app.services.review_service import ReviewService
from app.models.schemas import Notice

router = APIRouter()
review_svc = ReviewService()

@router.post("/notice/check")
def check_notice(title: str, content: str):
    review = review_svc.check_notice(title, content)
    notice = Notice(
        id=f"notice_{len(title)}",
        title=title,
        content=content
    )
    return {"notice": notice, "review": review}