import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
from ...database.session import get_db
from ...models.domain import Document, User
from ...security.auth import get_current_user
from ...ingestion.processor import sanitize_filename, ALLOWED_MIME_TYPES, extract_text_from_file, generate_chunks
from ...schemas.domain import DocumentResponse

router = APIRouter()

UPLOAD_DIR = "/tmp/manufacturing_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported file type")
        
    safe_filename = sanitize_filename(file.filename)
    file_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{safe_filename}")
    
    # Save file
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024: # 10MB limit
        raise HTTPException(status_code=413, detail="File too large")
        
    with open(file_path, "wb") as f:
        f.write(contents)
        
    # Check duplicate hash (simplified: just checking filename for now, in prod use MD5/SHA)
    existing = db.query(Document).filter(Document.filename == safe_filename).first()
    if existing:
        os.remove(file_path)
        raise HTTPException(status_code=409, detail="Duplicate document")
        
    doc = Document(
        id=file_id,
        filename=safe_filename,
        content_type=file.content_type,
        file_size=len(contents),
        uploaded_by=current_user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    return doc

@router.get("/", response_model=List[DocumentResponse])
def list_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Document).offset(skip).limit(limit).all()

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Only allow delete by owner or admin
    if doc.uploaded_by != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # Vector DB cleanup would go here
    # Graph cleanup would go here
    
    db.delete(doc)
    db.commit()
    return {"status": "deleted"}
