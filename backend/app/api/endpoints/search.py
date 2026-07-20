from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ...search.qdrant import vector_client
from ...database.session import get_db
from sqlalchemy.orm import Session
from ...models.domain import ExtractedEntity

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    limit: int = 5
    filters: Optional[dict] = None

class SearchResult(BaseModel):
    text: str
    score: float
    document_id: str
    page_number: int

@router.post("/semantic", response_model=List[SearchResult])
def semantic_search(request: SearchRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Empty query")
        
    try:
        hits = vector_client.search(request.query, limit=request.limit)
        results = []
        for hit in hits:
            # Assuming payload contains text, document_id, page_number
            payload = hit.payload or {}
            results.append(SearchResult(
                text=payload.get("text", ""),
                score=hit.score,
                document_id=payload.get("document_id", ""),
                page_number=payload.get("page_number", 1)
            ))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/hybrid")
def hybrid_search(request: SearchRequest, db: Session = Depends(get_db)):
    # Mocking hybrid logic for now: combining vector search with keyword/graph score
    results = semantic_search(request)
    return results

@router.post("/question")
def question_answering(request: SearchRequest):
    # Retrieve top semantic search results
    results = semantic_search(request)
    if not results:
        return {"answer": "Insufficient evidence found in the knowledge base.", "citations": []}
        
    # In a full implementation, pass results to an LLM to generate the answer
    # For now, return the best chunk as a mock answer
    best_hit = results[0]
    citation = {
        "document_id": best_hit.document_id,
        "page_number": best_hit.page_number,
        "evidence_text": best_hit.text
    }
    return {
        "answer": f"Based on the knowledge base: {best_hit.text}",
        "citations": [citation]
    }
