from langchain_openai import ChatOpenAI
from typing import Dict, Any
from app.core.config import config

class ReviewService:
    def __init__(self):
        self.llm = ChatOpenAI(model=config.llm_model, api_key=lambda: config.openai_api_key)

    def _response_text(self, response) -> str:
        content = getattr(response, "content", response)
        return content if isinstance(content, str) else str(content)

    def check_notice(self, title: str, content: str) -> Dict[str, str]:
        full_text = f"Title: {title}\nContent: {content}"
        prompt = f"Review this announcement for spelling errors, grammar issues, and suggest improvements. Provide corrected version if needed: {full_text}"
        response = self.llm.invoke(prompt)
        return {"review": self._response_text(response)}

    def assess_qna(self, question: str) -> Dict[str, Any]:
        prompt = f"""Assess this coding question's difficulty and assign points.
        Difficulty levels: easy (1-3 points), medium (4-7 points), hard (8-10 points).
        Return in format: Difficulty: [level], Points: [number]
        Question: {question}"""
        response = self.llm.invoke(prompt)
        text = self._response_text(response).lower()
        difficulty = "medium"
        points = 5
        if "easy" in text:
            difficulty = "easy"
            points = 2
        elif "hard" in text:
            difficulty = "hard"
            points = 9
        # Extract points if mentioned
        import re
        point_match = re.search(r'points?: (\d+)', text)
        if point_match:
            points = int(point_match.group(1))
        return {"difficulty": difficulty, "points": points}