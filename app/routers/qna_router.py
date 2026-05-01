import re
import logging
from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import config

router = APIRouter()
logger = logging.getLogger(__name__)


class QnaDifficultyRequest(BaseModel):
    title: str
    body: str


class QnaDifficultyResponse(BaseModel):
    score: int


@router.post("/qna/score", response_model=QnaDifficultyResponse)
async def score_qna_difficulty(request: QnaDifficultyRequest):
    plain_body = re.sub(r'<[^>]+>', '', request.body)[:2000]

    prompt = f"""아래 질문 게시글을 읽고 답변자 입장에서의 난이도를 1~10점으로 평가하세요.

평가 기준:
- 1~3점: 기초 질문 (검색으로 바로 해결 가능)
- 4~6점: 중급 질문 (어느 정도 경험 필요)
- 7~9점: 고급 질문 (깊은 전문 지식 필요)
- 10점: 전문가 수준 질문

규칙:
- 반드시 1에서 10 사이의 정수 하나만 반환할 것
- 다른 설명이나 문장은 절대 포함하지 말 것

[제목] {request.title}
[내용] {plain_body}
"""

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=config.gemini_api_key,
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip()
        logger.info("[LLM QnA 난이도] Gemini 응답=%s", raw)

        match = re.search(r'\b(10|[1-9])\b', raw)
        score = int(match.group(1)) if match else 5
        score = max(1, min(10, score))
    except Exception as e:
        logger.warning("[LLM QnA 난이도] 채점 실패, 기본값 5 반환. 원인=%s", e)
        score = 5

    return QnaDifficultyResponse(score=score)