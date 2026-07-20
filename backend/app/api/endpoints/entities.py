from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...database.session import get_db
from ...models.domain import ExtractedEntity, User
from ...security.auth import get_current_user
from ...schemas.domain import ExtractedEntityResponse
from ...graph.fuseki import fuseki_client
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD

router = APIRouter()

MFG = Namespace("http://example.org/manufacturing/")
PROV = Namespace("http://www.w3.org/ns/prov#")

from typing import List, Optional

@router.get("/", response_model=List[ExtractedEntityResponse])
def list_entities(skip: int = 0, limit: int = 100, status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(ExtractedEntity)
    if status:
        query = query.filter(ExtractedEntity.status == status.upper())
    return query.offset(skip).limit(limit).all()

@router.get("/{entity_id}", response_model=ExtractedEntityResponse)
def get_entity(entity_id: str, db: Session = Depends(get_db)):
    entity = db.query(ExtractedEntity).filter(ExtractedEntity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

@router.post("/{entity_id}/approve", response_model=ExtractedEntityResponse)
def approve_entity(entity_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    entity = db.query(ExtractedEntity).filter(ExtractedEntity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
        
    entity.status = "APPROVED"
    entity.graph_uri = f"http://example.org/manufacturing/entity/{entity.id}"
    db.commit()
    db.refresh(entity)
    
    # Insert to graph
    g = Graph()
    uri = URIRef(entity.graph_uri)
    
    # e.g., mfg:Machine
    class_uri = MFG[entity.entity_type]
    
    g.add((uri, RDF.type, class_uri))
    g.add((uri, MFG.entityLabel, Literal(entity.label, datatype=XSD.string)))
    g.add((uri, MFG.confidenceScore, Literal(entity.confidence, datatype=XSD.float)))
    
    # Provenance
    doc_uri = URIRef(f"http://example.org/manufacturing/document/{entity.document_id}")
    g.add((uri, MFG.describedIn, doc_uri))
    
    fuseki_client.insert_graph(g)
    
    return entity

@router.post("/{entity_id}/reject", response_model=ExtractedEntityResponse)
def reject_entity(entity_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    entity = db.query(ExtractedEntity).filter(ExtractedEntity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
        
    entity.status = "REJECTED"
    db.commit()
    db.refresh(entity)
    return entity
