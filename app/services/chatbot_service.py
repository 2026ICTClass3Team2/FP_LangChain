import os
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List
from app.core.config import config

class ChatbotService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=config.llm_model, 
            google_api_key=config.gemini_api_key
        )
        
        # Load clean code standards
        self.standards_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'clean_code_standards.md')
        self.clean_code_rules = ""
        try:
            with open(self.standards_path, 'r', encoding='utf-8') as f:
                self.clean_code_rules = f.read()
        except Exception as e:
            print(f"Warning: Could not load clean code standards. {e}")


    def _response_text(self, response) -> str:
        content = getattr(response, "content", response)
        return content if isinstance(content, str) else str(content)

    def review_code(self, code: str) -> str:
        prompt = f"""You are a senior software engineer. Please review the following code for best practices, bugs, and improvements.
        
Use the following Clean Code Standards as your primary reference:
---
{self.clean_code_rules}
---

Provide a cleaner and more efficient version of the code, and explain your reasoning.

Code to review:
{code}
"""
        response = self.llm.invoke(prompt)
        return self._response_text(response)

    def chat(self, message: str, history: List[str] = []) -> str:
        # Simple chat without memory for now
        history_str = "\n".join(history[-5:])  # Last 5 messages
        prompt = f"Previous conversation:\n{history_str}\n\nUser: {message}\nAssistant:"
        response = self.llm.invoke(prompt)
        return self._response_text(response)