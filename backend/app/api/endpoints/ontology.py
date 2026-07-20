from fastapi import APIRouter, Depends, HTTPException
from ...security.auth import get_current_user, require_role

router = APIRouter()

@router.get("/classes")
def list_classes():
    return {"classes": ["ManufacturingEntity", "Machine", "Process", "Material"]}

@router.get("/properties")
def list_properties():
    return {"properties": ["usesMachine", "producesProduct", "hasMeasurement"]}

@router.post("/classes")
def create_class(class_name: str, current_user = Depends(require_role(["admin"]))):
    # In real app, adds to the RDF ontology
    return {"status": "created", "class_name": class_name}

@router.post("/properties")
def create_property(prop_name: str, current_user = Depends(require_role(["admin"]))):
    return {"status": "created", "property_name": prop_name}
