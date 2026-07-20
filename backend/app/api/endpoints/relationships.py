from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...database.session import get_db
from ...models.domain import ExtractedRelationship, User
from ...security.auth import get_current_user
from ...schemas.domain import ExtractedRelationshipResponse

router = APIRouter()

@router.get("/", response_model=List[ExtractedRelationshipResponse])
def list_relationships(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ExtractedRelationship).offset(skip).limit(limit).all()

@router.post("/{rel_id}/approve", response_model=ExtractedRelationshipResponse)
def approve_relationship(rel_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rel = db.query(ExtractedRelationship).filter(ExtractedRelationship.id == rel_id).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")
        
    rel.status = "APPROVED"
    db.commit()
    db.refresh(rel)
    
    # In a full implementation, insert relationship to Graph database here
    # Requires fetching source and target URIs
    
    return rel

@router.post("/{rel_id}/reject", response_model=ExtractedRelationshipResponse)
def reject_relationship(rel_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rel = db.query(ExtractedRelationship).filter(ExtractedRelationship.id == rel_id).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")
        
    rel.status = "REJECTED"
    db.commit()
    db.refresh(rel)
    return rel
