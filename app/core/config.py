import os
from pydantic import BaseModel
from typing import List

class Config(BaseModel):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_model: str = ""
    allowed_tags: List[str] = [
        "python", "ml", "web", "devops", "notice", "study", "qna", "feed",
        "javascript", "react", "node", "ai", "data", "security", "cloud"
    ]

config = Config()