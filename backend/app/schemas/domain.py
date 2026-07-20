from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class ExtractedEntityBase(BaseModel):
    label: str
    entity_type: str
    confidence: float
    evidence_text: Optional[str] = None
    page_number: Optional[int] = None

class ExtractedEntityCreate(ExtractedEntityBase):
    document_id: str

class ExtractedEntityResponse(ExtractedEntityBase):
    id: str
    document_id: str
    status: str
    graph_uri: Optional[str] = None

    class Config:
        from_attributes = True

class ExtractedRelationshipBase(BaseModel):
    relation_type: str
    confidence: float
    evidence_text: Optional[str] = None

class ExtractedRelationshipCreate(ExtractedRelationshipBase):
    source_entity_id: str
    target_entity_id: str

class ExtractedRelationshipResponse(ExtractedRelationshipBase):
    id: str
    source_entity_id: str
    target_entity_id: str
    status: str
    
    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    filename: str
    content_type: str
    file_size: int

class DocumentResponse(DocumentBase):
    id: str
    status: str
    uploaded_at: datetime
    uploaded_by: Optional[int] = None

    class Config:
        from_attributes = True

class TextChunkBase(BaseModel):
    page_number: Optional[int]
    text: str
    chunk_index: int

class TextChunkResponse(TextChunkBase):
    id: str
    document_id: str
    vector_id: Optional[str] = None

    class Config:
        from_attributes = True

class GraphStatisticsResponse(BaseModel):
    classes: dict
    total_triples: int
