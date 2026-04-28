import logging
from typing import TypedDict, List

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from app.core.config import config

logger = logging.getLogger(__name__)


class TagState(TypedDict):
    title: str
    body: str
    available_tags: List[str]
    selected_tags: List[str]
    retry_count: int


def _get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=config.gemini_api_key,
    )


def call_llm(state: TagState) -> TagState:
    plain_body = state["body"][:3000]  # 내용 기반 판단을 위해 더 많이 읽음
    logger.info("[LLM 태그] Gemini 호출. 제목=%s, 태그목록=%s", state["title"], state["available_tags"])

    prompt = f"""
아래 게시글의 [내용]을 꼼꼼히 읽고, 내용에서 언급되거나 사용된 기술·언어·도구를 기준으로 태그를 선택하세요.
[제목]은 참고용이며, 반드시 [내용]에 근거하여 판단하세요.

선택 규칙:
- 반드시 [사용 가능한 태그 목록]에 있는 태그명만 사용할 것
- 최대 5개, 쉼표(,)로만 구분하여 태그명만 반환할 것
- 내용에 명확히 관련된 태그만 선택하고, 억측하지 말 것
- 다른 설명이나 문장은 절대 포함하지 말 것

[제목] {state["title"]}

[내용]
{plain_body}

[사용 가능한 태그 목록]
{", ".join(state["available_tags"])}
"""
    llm = _get_llm()
    response = llm.invoke([HumanMessage(content=prompt)])
    raw = response.content.strip()
    logger.info("[LLM 태그] Gemini 원본 응답=%s", raw)

    selected = [
        t.strip()
        for t in raw.split(",")
        if t.strip() in state["available_tags"]
    ]
    logger.info("[LLM 태그] 필터 후 선택 태그=%s", selected)

    return {**state, "selected_tags": selected[:5]}


def validate(state: TagState) -> TagState:
    return state


def increment_retry(state: TagState) -> TagState:
    return {**state, "retry_count": state["retry_count"] + 1}


def should_retry(state: TagState) -> str:
    if len(state["selected_tags"]) == 0 and state["retry_count"] < 2:
        return "retry"
    return "end"


def build_graph():
    graph = StateGraph(TagState)

    graph.add_node("call_llm", call_llm)
    graph.add_node("validate", validate)
    graph.add_node("retry", increment_retry)

    graph.set_entry_point("call_llm")
    graph.add_edge("call_llm", "validate")
    graph.add_conditional_edges(
        "validate",
        should_retry,
        {"retry": "retry", "end": END},
    )
    graph.add_edge("retry", "call_llm")

    return graph.compile()
