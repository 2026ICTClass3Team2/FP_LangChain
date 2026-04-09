import requests
import json
from langchain_openai import ChatOpenAI
from typing import Any, Dict, List
from app.core.config import config

class SummaryService:
    def __init__(self):
        self.llm = ChatOpenAI(model=config.llm_model, api_key=lambda: config.openai_api_key)

    def _response_text(self, response) -> str:
        content = getattr(response, "content", response)
        return content if isinstance(content, str) else str(content)

    def summarize_feed(self, link: str) -> Dict[str, Any]:
        # Fetch webpage content
        try:
            response = requests.get(link, timeout=10)
            content = response.text[:3000]  # Limit content length
        except Exception as e:
            content = f"Error fetching content: {str(e)}"

        prompt = f"Summarize the main content of this webpage in 2-3 sentences: {content}"
        summary_response = self.llm.invoke(prompt)
        summary = self._response_text(summary_response)

        tags = self.extract_tags(content + " " + summary)
        return {"summary": summary, "tags": tags}

    def extract_tags(self, text: str) -> List[str]:
        prompt = f"Extract up to 5 relevant tags from this text, choosing from these options: {', '.join(config.allowed_tags)}. Return as comma-separated list: {text[:1500]}"
        response = self.llm.invoke(prompt)
        tag_str = self._response_text(response)
        tags = [t.strip() for t in tag_str.split(',') if t.strip() in config.allowed_tags]
        return tags[:5]  # Limit to 5

    def breakdown_study(self, content: str) -> List[Dict[str, str]]:
        prompt = f"""Break down this study material into logical chapters.
        Return as a JSON array of objects, each with 'title' and 'content' keys.
        Example: [{"title": "Chapter 1", "content": "Content here"}]
        Material: {content[:2000]}"""
        response = self.llm.invoke(prompt)
        try:
            chapters = json.loads(self._response_text(response))
        except:
            chapters = [{"title": "Full Content", "content": content}]
        return chapters

    def translate_content(self, content: str, target_lang: str = "english") -> str:
        prompt = f"Translate the following text to {target_lang}: {content[:1000]}"
        response = self.llm.invoke(prompt)
        return self._response_text(response)