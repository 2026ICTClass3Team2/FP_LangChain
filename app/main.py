from fastapi import FastAPI
from app.routers.feed_router import router as feed_router
from app.routers.study_router import router as study_router
from app.routers.qna_router import router as qna_router
from app.routers.notice_router import router as notice_router
from app.routers.chatbot_router import router as chatbot_router

app = FastAPI(title="FP LangChain Web Service", version="1.0.0")

app.include_router(feed_router, prefix="/api", tags=["feed"])
app.include_router(study_router, prefix="/api", tags=["study"])
app.include_router(qna_router, prefix="/api", tags=["qna"])
app.include_router(notice_router, prefix="/api", tags=["notice"])
app.include_router(chatbot_router, prefix="/api", tags=["chatbot"])

@app.get("/")
def root():
    return {"message": "Welcome to FP LangChain Web Service"}