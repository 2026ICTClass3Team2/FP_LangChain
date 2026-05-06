import json
import logging
import random
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.core.config import config

logger = logging.getLogger(__name__)

_TOPICS = [
    "알고리즘", "자료구조", "Java", "Python", "Spring Boot", "React",
    "데이터베이스 최적화", "네트워크", "운영체제", "디자인 패턴",
    "동시성·멀티스레딩", "REST API 설계", "Docker·컨테이너", "SQL 튜닝",
    "JavaScript", "TypeScript", "Git 워크플로", "CI/CD", "보안(JWT·OAuth)",
    "캐싱 전략", "함수형 프로그래밍", "메모리 관리",
]

_FALLBACK_QUESTIONS = [
    {
        "title": "[이벤트] 배열에서 두 수의 합 찾기",
        "body": (
            "정수 배열 nums와 목표값 target이 주어질 때, 합이 target이 되는 "
            "두 원소의 인덱스를 반환하는 함수를 작성하세요.\n\n"
            "예시:\n  nums = [2, 7, 11, 15], target = 9\n  반환값: [0, 1]\n\n"
            "시간복잡도 O(n) 해법을 설명하고 코드로 구현해 보세요."
        ),
        "difficulty": "easy",
        "points": 10,
    },
    {
        "title": "[이벤트] LRU 캐시 구현하기",
        "body": (
            "용량(capacity)이 제한된 LRU(Least Recently Used) 캐시를 구현하세요.\n\n"
            "- get(key): 키가 존재하면 값 반환, 없으면 -1\n"
            "- put(key, value): 키-값 삽입, 용량 초과 시 가장 오래 미사용된 항목 제거\n\n"
            "두 연산 모두 O(1) 시간복잡도를 만족해야 합니다. "
            "사용한 자료구조와 그 이유를 설명하세요."
        ),
        "difficulty": "medium",
        "points": 15,
    },
    {
        "title": "[이벤트] CAP 이론과 분산 데이터베이스 설계",
        "body": (
            "CAP 이론(Consistency, Availability, Partition Tolerance)을 설명하고, "
            "실제 분산 데이터베이스(예: Cassandra, MongoDB, etcd)가 각 속성을 어떻게 "
            "트레이드오프하는지 구체적인 예를 들어 설명하세요.\n\n"
            "네트워크 파티션이 발생했을 때 시스템이 어떻게 동작해야 하는지, "
            "그리고 최종 일관성(Eventual Consistency) 모델의 한계와 보완 방법도 논하세요."
        ),
        "difficulty": "hard",
        "points": 20,
    },
]


class EventQnaService:
    def __init__(self) -> None:
        self.llm = ChatGoogleGenerativeAI(
            model=config.llm_model,
            google_api_key=config.gemini_api_key,
        )

    def verify_answer(self, question_title: str, question_body: str, comment_body: str) -> bool:
        """Returns True if the comment genuinely answers the question."""
        prompt = f"""당신은 개발자 Q&A 플랫폼의 채점자입니다.
아래 질문에 대해 제출된 답변이 실제로 질문에 대한 유효한 답변인지 판단하세요.

[질문 제목]
{question_title}

[질문 내용]
{question_body}

[제출된 답변]
{comment_body}

판단 기준:
- 답변이 질문의 핵심 내용을 다루고 있는가
- 기술적으로 올바른 정보를 포함하고 있는가
- 단순한 인사말, 질문 재반복, 관련 없는 내용이 아닌가
- 최소한의 설명 또는 코드가 포함되어 있는가

"yes" 또는 "no" 중 하나만 답하세요. 다른 텍스트는 포함하지 마세요."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            answer = response.content.strip().lower()
            logger.info("[이벤트 QnA 검증] 응답='%s'", answer)
            return answer.startswith("yes")
        except Exception as e:
            logger.warning("[이벤트 QnA 검증] LLM 호출 실패: %s", e)
            return False

    def generate_event_questions(self) -> list[dict]:
        today = datetime.now().strftime("%Y년 %m월 %d일")
        topics = random.sample(_TOPICS, 3)

        prompt = f"""오늘({today})의 개발자 커뮤니티 주간 이벤트 Q&A 문제 3개를 생성해주세요.
각 문제는 실제 기술 인터뷰나 실무에서 마주칠 수 있는 실용적인 질문이어야 합니다.

주제 (순서대로 사용):
1. {topics[0]} → 난이도: 쉬움 (easy), 포인트: 10
2. {topics[1]} → 난이도: 보통 (medium), 포인트: 15
3. {topics[2]} → 난이도: 어려움 (hard), 포인트: 20

반환 형식 (JSON 배열만, 다른 텍스트 없이):
[
  {{
    "title": "[이벤트] 질문 제목 (간결하고 명확하게, 50자 이내)",
    "body": "질문 상세 내용 (배경·조건·예시 포함, 일반 텍스트, 200자 이상)",
    "difficulty": "easy",
    "points": 10
  }},
  {{
    "title": "[이벤트] 질문 제목",
    "body": "질문 상세 내용",
    "difficulty": "medium",
    "points": 15
  }},
  {{
    "title": "[이벤트] 질문 제목",
    "body": "질문 상세 내용",
    "difficulty": "hard",
    "points": 20
  }}
]

규칙:
- 제목은 반드시 "[이벤트]"로 시작할 것
- body는 HTML 태그 없이 일반 텍스트로 작성
- 매주 다른 문제가 나오도록 창의적으로 생성
- JSON 배열만 반환, 마크다운 코드블록(```) 없이"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            raw = response.content.strip()
            logger.info("[이벤트 QnA] LLM 응답 길이=%d", len(raw))

            start = raw.find("[")
            end = raw.rfind("]") + 1
            if start == -1 or end <= 0:
                raise ValueError("JSON array not found in LLM response")

            parsed: list[dict] = json.loads(raw[start:end])

            difficulties = ["easy", "medium", "hard"]
            points_map = {"easy": 10, "medium": 15, "hard": 20}
            result = []
            for i, q in enumerate(parsed[:3]):
                diff = difficulties[i]
                result.append({
                    "title": str(q.get("title", f"[이벤트] 문제 {i + 1}"))[:255],
                    "body": str(q.get("body", "문제 내용을 불러오지 못했습니다.")),
                    "difficulty": diff,
                    "points": points_map[diff],
                })
            logger.info("[이벤트 QnA] %d개 문제 생성 완료", len(result))
            return result

        except Exception as e:
            logger.warning("[이벤트 QnA] 생성 실패, 기본 문제 반환. 원인=%s", e)
            return _FALLBACK_QUESTIONS
