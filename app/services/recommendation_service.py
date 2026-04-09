from typing import List
from app.models.schemas import Feed

class RecommendationService:
    def recommend_feeds(self, user_interests: List[str], feeds: List[Feed]) -> List[Feed]:
        # Simple tag-based recommendation: sort feeds by number of matching tags
        def score(feed: Feed) -> int:
            return len(set(user_interests) & set(feed.tags))
        return sorted(feeds, key=score, reverse=True)