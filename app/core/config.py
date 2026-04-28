import os
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드 (다른 모듈보다 먼저 실행되어야 함)

class Config(BaseModel):
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    llm_model: str = "gemini-2.5-flash"
    allowed_tags: List[str] = [
        "python", "ml", "web", "devops", "notice", "study", "qna", "feed",
        "javascript", "react", "node", "ai", "data", "security", "cloud"
    ]

config = Config()