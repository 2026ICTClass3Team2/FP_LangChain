from fastapi import APIRouter
from app.services.summary_service import SummaryService
from app.models.schemas import Study

router = APIRouter()
summary_svc = SummaryService()

@router.post("/study/breakdown")
def breakdown_study(title: str, content: str):
    chapters = summary_svc.breakdown_study(content)
    study = Study(
        id=f"study_{title.replace(' ', '_')}",
        title=title,
        content=content,
        chapters=chapters
    )
    return study

@router.post("/study/translate")
def translate_study(content: str, target_lang: str = "english"):
    translated = summary_svc.translate_content(content, target_lang)
    return {"translated": translated}