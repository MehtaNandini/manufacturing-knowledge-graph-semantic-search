from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from ...security.auth import get_current_user, require_role
from ...graph.fuseki import fuseki_client

router = APIRouter()

class SparqlQuery(BaseModel):
    query: str

@router.get("/statistics")
def get_statistics():
    try:
        stats = fuseki_client.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sparql")
def run_sparql(
    query_obj: SparqlQuery = Body(...),
    current_user = Depends(get_current_user)
):
    query = query_obj.query
    
    # Security check: Viewer role can only run SELECT/ASK/DESCRIBE/CONSTRUCT
    if current_user.role.value == "viewer":
        query_upper = query.upper()
        if "INSERT" in query_upper or "DELETE" in query_upper or "UPDATE" in query_upper or "DROP" in query_upper:
            raise HTTPException(status_code=403, detail="Viewer role can only run read-only SPARQL queries")
            
    try:
        if any(keyword in query.upper() for keyword in ["INSERT", "DELETE", "UPDATE", "DROP"]):
            fuseki_client.update(query)
            return {"status": "Update successful"}
        else:
            results = fuseki_client.query(query)
            return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SPARQL Error: {str(e)}")
