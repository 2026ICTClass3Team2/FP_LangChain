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
        
        # Load clean code standards from PDF
        # We use pypdf to read the PDF file and extract text from each page
        self.standards_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'Clean_Code.pdf')
        self.clean_code_rules = ""
        try:
            import pypdf
            # Open the PDF file in binary read mode
            with open(self.standards_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                # Iterate through all pages and concatenate the extracted text
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        self.clean_code_rules += text + "\n"
        except Exception as e:
            print(f"Warning: Could not load clean code standards from PDF. {e}")


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