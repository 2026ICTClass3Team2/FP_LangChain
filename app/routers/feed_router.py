from fastapi import APIRouter
from typing import Any, List, cast
from app.services.summary_service import SummaryService
from app.services.recommendation_service import RecommendationService
from app.models.schemas import Feed, User

router = APIRouter()
summary_svc = SummaryService()
rec_svc = RecommendationService()

# In-memory storage for demo
feeds: List[Feed] = []
users: List[User] = []

@router.post("/api/feed/summarize")
def summarize_feed(link: str, author_id: str):
    result = summary_svc.summarize_feed(link)
    feed = Feed(
        id=f"feed_{len(feeds)+1}",
        title="Auto-generated",  # Could extract from link
        link=link,
        summary=result["summary"],
        tags=cast(List[str], result["tags"]),
        author_id=author_id
    )
    feeds.append(feed)
    return feed

@router.get("/api/feed/recommend/{user_id}")
def recommend_feeds(user_id: str):
    user = next((u for u in users if u.id == user_id), None)
    if not user:
        return []
    return rec_svc.recommend_feeds(user.interests, feeds)

@router.post("/api/user")
def create_user(user: User):
    users.append(user)
    return user