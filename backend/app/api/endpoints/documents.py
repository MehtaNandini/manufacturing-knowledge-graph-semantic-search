import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
from ...database.session import get_db, SessionLocal
from ...models.domain import Document, User, ExtractedEntity
from ...security.auth import get_current_user
from ...ingestion.processor import sanitize_filename, ALLOWED_MIME_TYPES, extract_text_from_file, generate_chunks
from ...schemas.domain import DocumentResponse
from ...extraction.nlp_pipeline import extract_entities
from ...search.qdrant import vector_client

router = APIRouter()

UPLOAD_DIR = "/tmp/manufacturing_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def process_document_task(file_path: str, mime_type: str, document_id: str):
    db = SessionLocal()
    try:
        pages = extract_text_from_file(file_path, mime_type)
        chunks = generate_chunks(pages)
        
        for chunk in chunks:
            # 1. Insert to Qdrant
            try:
                vector_client.insert_chunk(
                    chunk_id=chunk["id"], 
                    text=chunk["text"], 
                    payload={"document_id": document_id, "page_number": chunk["page_number"]}
                )
            except Exception as e:
                print(f"Failed to insert chunk to Qdrant: {e}")
            
            # 2. Extract Entities
            extracted = extract_entities(chunk["text"], chunk["page_number"])
            for ent in extracted:
                db_ent = ExtractedEntity(
                    id=str(uuid.uuid4()),
                    document_id=document_id,
                    entity_type=ent["entity_type"],
                    label=ent["label"],
                    confidence=ent["confidence"],
                    evidence_text=ent["evidence_text"],
                    page_number=ent["page_number"],
                    status="PENDING"
                )
                db.add(db_ent)
        
        db.commit()
    except Exception as e:
        print(f"Error processing document {document_id}: {e}")
        db.rollback()
    finally:
        db.close()

@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
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
    
    # Trigger background NLP extraction
    background_tasks.add_task(process_document_task, file_path, file.content_type, doc.id)
    
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
