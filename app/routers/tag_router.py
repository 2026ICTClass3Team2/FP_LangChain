from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from app.graph.tag_graph import build_graph

router = APIRouter()
tag_graph = build_graph()


class TagSuggestionRequest(BaseModel):
    title: str
    body: str
    available_tags: List[str]


class TagSuggestionResponse(BaseModel):
    tags: List[str]


@router.post("/tags/suggest", response_model=TagSuggestionResponse)
async def suggest_tags(request: TagSuggestionRequest):
    if not request.available_tags:
        raise HTTPException(status_code=400, detail="태그 목록이 비어 있습니다.")

    try:
        result = tag_graph.invoke({
            "title": request.title,
            "body": request.body,
            "available_tags": request.available_tags,
            "selected_tags": [],
            "retry_count": 0,
        })
        return TagSuggestionResponse(tags=result["selected_tags"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
