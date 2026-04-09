from langchain_openai import ChatOpenAI
from typing import List
from app.core.config import config

class ChatbotService:
    def __init__(self):
        self.llm = ChatOpenAI(model=config.llm_model, api_key=lambda: config.openai_api_key)

    def _response_text(self, response) -> str:
        content = getattr(response, "content", response)
        return content if isinstance(content, str) else str(content)

    def review_code(self, code: str) -> str:
        prompt = f"Please review the following code for best practices, bugs, and improvements:\n\n{code}"
        response = self.llm.invoke(prompt)
        return self._response_text(response)

    def chat(self, message: str, history: List[str] = []) -> str:
        # Simple chat without memory for now
        history_str = "\n".join(history[-5:])  # Last 5 messages
        prompt = f"Previous conversation:\n{history_str}\n\nUser: {message}\nAssistant:"
        response = self.llm.invoke(prompt)
        return self._response_text(response)