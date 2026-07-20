from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import time
from uuid import uuid4
from .api.endpoints import auth, documents, entities, relationships, graph, search, ontology, quality
from .database.session import engine
from .models import domain
from .models.base import Base

# Create database tables
Base.metadata.create_all(bind=engine)
# Setup basic FastAPI app
app = FastAPI(
    title="Manufacturing Knowledge Graph API",
    description="Full stack semantic modelling and machine learning platform API",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware for structured logging and request IDs
@app.middleware("http")
async def add_request_id_and_log(request, call_next):
    request_id = str(uuid4())
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(entities.router, prefix="/api/entities", tags=["Entities"])
app.include_router(relationships.router, prefix="/api/relationships", tags=["Relationships"])
app.include_router(graph.router, prefix="/api/graph", tags=["Knowledge Graph"])
app.include_router(search.router, prefix="/api/search", tags=["Semantic Search"])
app.include_router(ontology.router, prefix="/api/ontology", tags=["Ontology"])
app.include_router(quality.router, prefix="/api/quality", tags=["Quality"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Manufacturing KG"}

@app.get("/ready")
def readiness_check():
    return {"status": "ready"}

@app.get("/metrics")
def metrics():
    return {"status": "metrics_endpoint_stub"}
