from langchain_openai import ChatOpenAI
from typing import List
from app.core.config import config

class TagService:
    def __init__(self):
        self.llm = ChatOpenAI(model=config.llm_model, api_key=lambda: config.openai_api_key)

    def _normalize_response(self, response) -> str:
        content = getattr(response, "content", response)
        if isinstance(content, str):
            return content
        return str(content)

    def extract_tags(self, text: str) -> List[str]:
        prompt = f"Extract up to 5 relevant tags from this text, choosing from these options: {', '.join(config.allowed_tags)}. Return as comma-separated list: {text[:1500]}"
        response = self.llm.invoke(prompt)
        tag_str = self._normalize_response(response)
        tags = [t.strip() for t in tag_str.split(',') if t.strip() in config.allowed_tags]
        return tags[:5]