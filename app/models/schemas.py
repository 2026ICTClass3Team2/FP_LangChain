from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional

class User(BaseModel):
    id: str
    interests: List[str] = []  # Tags user is interested in

class TaggedContent(BaseModel):
    id: str
    tags: List[str] = []
    created_at: datetime = datetime.now()

class Feed(TaggedContent):
    title: str
    link: str
    summary: str = ""
    author_id: str

class Study(TaggedContent):
    title: str
    content: str  # Original markdown or pdf content
    chapters: List[Dict[str, str]] = []  # List of {"title": "", "content": ""}
    translated_content: Optional[str] = None

class QnA(TaggedContent):
    question: str
    answer: str = ""
    difficulty: str = "easy"  # easy, medium, hard
    points: int = 0

class Notice(TaggedContent):
    title: str
    content: str
    priority: str = "normal"  # low, normal, high
    expires_at: Optional[datetime] = None