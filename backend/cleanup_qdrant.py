import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup Postgres
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "manufacturing_kg")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

sys.path.append("/app")

# Setup Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
COLLECTION_NAME = "manufacturing_chunks"

def run_cleanup():
    db = SessionLocal()
    # Get all active document IDs
    from app.models.domain import Document
    active_docs = db.query(Document).all()
    active_ids = {doc.id for doc in active_docs}
    db.close()
    
    # Scroll through Qdrant
    points, next_page = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=10000,
        with_payload=True
    )
    
    to_delete = []
    for point in points:
        doc_id = point.payload.get("document_id")
        if not doc_id or doc_id not in active_ids:
            to_delete.append(point.id)
            
    if to_delete:
        print(f"Deleting {len(to_delete)} orphaned chunks from Qdrant...")
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=to_delete
        )
        print("Done.")
    else:
        print("No orphaned chunks found.")

if __name__ == "__main__":
    run_cleanup()
