from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .base import Base

class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    RESEARCHER = "researcher"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True)

class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, index=True) # UUID
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    file_size = Column(Integer)
    status = Column(String, default="UPLOADED") # UPLOADED, PROCESSING, COMPLETED, FAILED
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("TextChunk", back_populates="document", cascade="all, delete-orphan")
    entities = relationship("ExtractedEntity", back_populates="document", cascade="all, delete-orphan")

class DocumentPage(Base):
    __tablename__ = "document_pages"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"))
    page_number = Column(Integer, nullable=False)
    text_content = Column(String)
    
    document = relationship("Document", back_populates="pages")

class TextChunk(Base):
    __tablename__ = "text_chunks"
    id = Column(String, primary_key=True, index=True) # UUID
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"))
    page_number = Column(Integer)
    text = Column(String, nullable=False)
    chunk_index = Column(Integer)
    vector_id = Column(String) # Reference to Qdrant ID
    
    document = relationship("Document", back_populates="chunks")

class ExtractedEntity(Base):
    __tablename__ = "extracted_entities"
    id = Column(String, primary_key=True, index=True) # UUID
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"))
    label = Column(String, nullable=False)
    entity_type = Column(String, nullable=False) # e.g., Machine, Process
    confidence = Column(Float)
    evidence_text = Column(String)
    page_number = Column(Integer)
    status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED
    graph_uri = Column(String)
    
    document = relationship("Document", back_populates="entities")
    source_relations = relationship("ExtractedRelationship", foreign_keys="ExtractedRelationship.source_entity_id", back_populates="source_entity")
    target_relations = relationship("ExtractedRelationship", foreign_keys="ExtractedRelationship.target_entity_id", back_populates="target_entity")

class ExtractedRelationship(Base):
    __tablename__ = "extracted_relationships"
    id = Column(String, primary_key=True, index=True) # UUID
    source_entity_id = Column(String, ForeignKey("extracted_entities.id", ondelete="CASCADE"))
    target_entity_id = Column(String, ForeignKey("extracted_entities.id", ondelete="CASCADE"))
    relation_type = Column(String, nullable=False) # e.g., usesMachine
    confidence = Column(Float)
    evidence_text = Column(String)
    status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED
    
    source_entity = relationship("ExtractedEntity", foreign_keys=[source_entity_id], back_populates="source_relations")
    target_entity = relationship("ExtractedEntity", foreign_keys=[target_entity_id], back_populates="target_relations")
