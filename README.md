# FP_LangChain — DeadBug LLM Service

FastAPI microservice that wraps Google's **Gemini 2.5 Flash Lite** for the DeadBug platform. Called by the Spring Boot backend over HTTP via `WebClient`. Hosts tag suggestion, QnA difficulty scoring, chatbot/code-review, and weekly event-QnA generation.

## Tech stack

- **FastAPI 0.135** on **Python 3.11**
- **LangChain 1.2** + **LangGraph 1.1** (retry state machine for tag suggestion)
- **langchain-google-genai** → **Gemini 2.5 Flash Lite**
- **Pydantic 2** for request/response schemas
- **uvicorn** ASGI server (port `8001`)

## Prerequisites

- Python 3.11
- A Gemini API key

## Quick start

```bash
pip install -r requirements.txt
# Set GEMINI_API_KEY in a .env file at FP_LangChain/.env, then:
python main.py             # uvicorn on http://0.0.0.0:8001

# Verify syntactic health without running:
python -c "import app.main"
```

There is no test runner configured.

## Environment variables

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key. Loaded from `.env` by `python-dotenv`. |

Configured in `app/core/config.py`. The model name (`gemini-2.5-flash-lite`) and the allowed-tag list are also defined there.

## Project structure

```
FP_LangChain/
  main.py                        Uvicorn entry point (port 8001)
  requirements.txt
  Dockerfile
  Jenkinsfile
  app/
    main.py                      FastAPI app, CORS, router mounts
    core/
      config.py                  Pydantic Config: gemini_api_key, llm_model, allowed_tags
    routers/
      tag_router.py              POST /api/tags/suggest        (LangGraph)
      qna_router.py              POST /api/qna/score
      chatbot_router.py          POST /api/chatbot/review, POST /api/chatbot/chat
      event_router.py            POST /api/event/generate, POST /api/event/verify
    services/
      chatbot_service.py         System prompts + chat logic (code review, general Q&A)
      event_service.py           Event QnA generation and answer verification
    graph/
      tag_graph.py               LangGraph state machine with retry-on-invalid-tags
    models/
      schemas.py                 Pydantic models (currently unused, kept as scaffolding)
  data/                          Local data fixtures (if any)
```

## Endpoints

All routers are mounted under `/api`. The Spring backend is the only caller.

| Method + path | Purpose | Backend caller |
|---|---|---|
| `POST /api/tags/suggest` | Suggest up to 5 tags for post content; LangGraph retries on invalid output | `LlmTagService` |
| `POST /api/qna/score` | Score a QnA question (difficulty 1–10) | `LlmQnaService` |
| `POST /api/chatbot/review` | Clean-Code-style code review | `ChatbotService` |
| `POST /api/chatbot/chat` | General platform chatbot | `ChatbotService` |
| `POST /api/event/generate` | Generate weekly event QnA questions | `EventQnaScheduler` (daily cron) |
| `POST /api/event/verify` | Verify an event QnA answer | `EventQnaVerificationService` |
| `GET /` | Welcome JSON | (none) |
| `GET /health` | Liveness probe | (deployment) |

## LangGraph tag suggestion

`app/graph/tag_graph.py` defines a state machine:

1. Ask Gemini to extract up to 5 tags from post text
2. Filter the response against `allowed_tags` in `app/core/config.py`
3. If zero valid tags are returned, retry up to N times
4. Return the final tag list

**To add a new tag** edit the `allowed_tags` list in `app/core/config.py` — do not put it in the prompt.

## Adding a new endpoint

```python
# 1. Add request/response schema to app/models/schemas.py or inline in the router
# 2. Service logic in app/services/<name>_service.py
# 3. Router in app/routers/<name>_router.py
# 4. Mount it in app/main.py:
#    app.include_router(<name>_router, prefix="/api", tags=["<name>"])
```
