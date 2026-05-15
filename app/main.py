from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.qna_router import router as qna_router
from app.routers.chatbot_router import router as chatbot_router
from app.routers.tag_router import router as tag_router
from app.routers.event_router import router as event_router

app = FastAPI(title="FP LangChain Web Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(qna_router, prefix="/api", tags=["qna"])
app.include_router(chatbot_router, prefix="/api", tags=["chatbot"])
app.include_router(tag_router, prefix="/api", tags=["tag"])
app.include_router(event_router, prefix="/api", tags=["event"])

@app.get("/")
def root():
    return {"message": "Welcome to FP LangChain Web Service"}

@app.get("/health")
def health():
    return {"status": "ok"}