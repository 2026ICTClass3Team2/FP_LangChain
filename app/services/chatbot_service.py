import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.prebuilt import create_react_agent
from typing import List
from app.core.config import config

_FAQ_SECTIONS: dict[str, str] = {
    "기능": """DeadBug의 주요 기능:
- 피드(Feed): 게시글 작성·공유, 팔로우 기반 개인화 피드, AI 자동 태그 부여, 채널 구독
- QnA 게시판: 기술 질문과 답변, AI 난이도 채점(1~10점), 답변 채택 시 포인트 지급
- 학습(Study): 채널별 학습 자료 열람, PDF 뷰어 지원
- 실시간 채팅: WebSocket 기반 1:1 다이렉트 메시지
- AI 비서: FAQ 챗봇과 클린 코드 분석기
- 채널(Channel): 주제별 채널 구독·알림
- 포인트 시스템: QnA 답변 채택 시 포인트 획득, 포인트 상점 이용
- 포인트 상점: 이모티콘·아이템 구매""",
    "포인트": """포인트 시스템:
- QnA 답변이 채택되면 AI 난이도 점수(1~10)와 질문자 설정 보상 포인트의 합산을 받습니다.
- 이벤트 QnA(주 1회 AI 생성)의 첫 번째 답변자에게는 이벤트 포인트(10~20P)가 자동 지급됩니다.
- 획득한 포인트는 포인트 상점에서 이모티콘 등 아이템 구매에 사용합니다.""",
    "채널": """채널 기능:
- 채널은 특정 주제(예: React, Spring Boot, 알고리즘)별 게시글 공간입니다.
- 채널을 구독하면 새 게시글이 올라올 때 알림을 받습니다.
- '채널 만들기' 버튼으로 직접 채널을 개설할 수 있습니다.""",
    "신고": """신고 기능:
- 게시글·댓글·유저의 더보기 메뉴(⋮)에서 '신고'를 클릭하면 관리자에게 접수됩니다.
- 관리자가 검토 후 경고, 게시글 삭제, 계정 정지 등 조치를 취합니다.""",
    "로그인": """로그인 방법:
- 이메일/비밀번호 로그인 또는 Google·Kakao·GitHub 소셜 로그인을 이용할 수 있습니다.""",
    "정지": """계정 정지:
- 이용 약관 위반 시 관리자가 계정을 정지할 수 있습니다.
- 정지된 계정은 서비스를 이용할 수 없으며, 로그인 시 정지 안내 및 해제 예정일이 표시됩니다.""",
    "멘션": """멘션(@) 기능:
- 게시글·댓글 에디터에서 @를 입력하면 유저 검색 팝업이 나타납니다.
- 원하는 유저를 선택하면 해당 유저에게 멘션 알림이 전송됩니다.""",
    "북마크": """북마크:
- 게시글 상세 화면의 북마크 아이콘을 클릭하면 저장됩니다.
- 저장된 게시글은 마이페이지 → 북마크에서 모아볼 수 있습니다.""",
    "코드리뷰": """AI 코드 분석기:
- 채팅 사이드바에서 AI 비서 탭을 선택하고 코드를 붙여넣은 후 '코드 분석 시작'을 누르세요.
- Clean Code 표준에 따라 AI가 코드를 리뷰하고 개선 방향을 제시합니다.""",
    "qna": """QnA 기능:
- 질문 작성자만 답변을 채택할 수 있습니다.
- 채택된 답변 작성자에게 AI 난이도 점수 + 질문자 설정 포인트가 지급됩니다.
- 이벤트 QnA는 주 1회 AI가 생성하며, 첫 번째 답변자에게 이벤트 포인트가 자동 지급됩니다.""",
    "팔로우": """팔로우 시스템:
- 유저·채널을 팔로우하면 해당 유저의 새 게시글이나 채널 알림을 받습니다.
- 마이페이지에서 팔로우한 유저와 채널 목록을 확인할 수 있습니다.""",
}

_KEYWORD_MAP: dict[str, list[str]] = {
    "기능":    ["기능", "feature", "서비스", "소개", "what"],
    "포인트":  ["포인트", "point", "보상", "적립", "이벤트 포인트"],
    "채널":    ["채널", "channel", "구독", "subscribe"],
    "신고":    ["신고", "report", "처리", "차단"],
    "로그인":  ["로그인", "login", "소셜", "google", "kakao", "github", "가입"],
    "정지":    ["정지", "ban", "suspend", "계정 정지"],
    "멘션":    ["멘션", "mention", "@"],
    "북마크":  ["북마크", "bookmark", "저장"],
    "코드리뷰":["코드", "code", "리뷰", "review", "분석", "clean"],
    "qna":     ["qna", "질문", "답변", "채택", "이벤트", "event"],
    "팔로우":  ["팔로우", "follow", "구독"],
}

_AGENT_SYSTEM = """당신은 DeadBug 개발자 커뮤니티 플랫폼의 AI 어시스턴트입니다.

플랫폼 관련 질문(기능·포인트·채널·QnA·신고·로그인 등)이 들어오면
반드시 search_deadbug_faq 툴을 먼저 호출하여 정확한 정보를 조회한 후 답변하세요.
항상 한국어로 친절하고 명확하게 답변하세요.
플랫폼과 무관한 일반 개발 질문에도 도움을 드릴 수 있지만,
이 챗봇이 주로 DeadBug 이용 안내를 위한 것임을 안내하세요."""


@tool
def search_deadbug_faq(query: str) -> str:
    """DeadBug 플랫폼의 기능·정책·이용 방법을 검색합니다.
    포인트, 채널, QnA, 신고, 로그인, 계정 정지, 멘션, 북마크,
    코드 리뷰, 팔로우, 이벤트 등 플랫폼 관련 질문에 사용하세요."""
    query_lower = query.lower()
    found: list[str] = []
    for key, kws in _KEYWORD_MAP.items():
        if any(kw in query_lower for kw in kws):
            found.append(_FAQ_SECTIONS[key])
    return "\n\n".join(found) if found else _FAQ_SECTIONS["기능"]


class ChatbotService:
    def __init__(self) -> None:
        self.llm = ChatGoogleGenerativeAI(
            model=config.llm_model,
            google_api_key=config.gemini_api_key,
        )

        # Load clean code standards from PDF
        standards_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data", "Clean_Code.pdf",
        )
        self.clean_code_rules = ""
        try:
            import pypdf
            with open(standards_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        self.clean_code_rules += text + "\n"
        except Exception as e:
            print(f"Warning: Could not load clean code standards. {e}")

        # ReAct agent for FAQ chat (langgraph.prebuilt)
        self._chat_agent = create_react_agent(
            model=self.llm,
            tools=[search_deadbug_faq],
            prompt=SystemMessage(content=_AGENT_SYSTEM),
        )

        # LCEL chain for code review (single-shot, no tool loop needed)
        review_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a senior software engineer. "
                "Review the following code using these Clean Code standards:\n"
                "{clean_code_rules}\n\n"
                "Provide a cleaner and more efficient version of the code, "
                "explain your reasoning, and list specific improvements. "
                "Reply in Korean.",
            ),
            ("human", "{code}"),
        ])
        self._review_chain = review_prompt | self.llm | StrOutputParser()

    def review_code(self, code: str) -> str:
        return self._review_chain.invoke({
            "clean_code_rules": self.clean_code_rules[:8000],
            "code": code,
        })

    def chat(self, message: str, history: List[str] = []) -> str:
        messages: list = []
        for i, h in enumerate(history[-10:]):
            messages.append(HumanMessage(content=h) if i % 2 == 0 else AIMessage(content=h))
        messages.append(HumanMessage(content=message))

        result = self._chat_agent.invoke({"messages": messages})
        return result["messages"][-1].content
