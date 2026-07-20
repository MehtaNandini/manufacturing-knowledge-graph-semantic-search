import spacy
from typing import List, Dict, Any
import re

# We use the small model. In production, a fine-tuned transformer or large model is preferred.
# Make sure to run `python -m spacy download en_core_web_sm` beforehand.
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Simple rule-based/dictionary-based extraction fallback for manufacturing domain
MANUFACTURING_MACHINES = ["CNC milling machine", "lathe", "laser cutter", "welding machine", "conveyor motor", "assembly robot"]
MANUFACTURING_MATERIALS = ["stainless steel", "aluminum", "titanium", "plastic", "carbide"]
MANUFACTURING_PROCESSES = ["welding", "milling", "cutting", "assembly", "inspection"]
MANUFACTURING_TOOLS = ["carbide cutting tool", "drill bit", "laser"]
MANUFACTURING_SENSORS = ["vibration sensor", "temperature sensor", "pressure sensor"]
MANUFACTURING_DEFECTS = ["surface defect", "crack", "porosity"]
MANUFACTURING_FAILURE_MODES = ["bearing wear", "overheating", "motor failure"]

def extract_entities(text: str, page_number: int = 1) -> List[Dict[str, Any]]:
    doc = nlp(text)
    entities = []
    
    text_lower = text.lower()
    
    # 1. Rule-based extraction (Domain Specific)
    for machine in MANUFACTURING_MACHINES:
        if machine in text_lower:
            entities.append({
                "label": machine,
                "entity_type": "Machine",
                "confidence": 0.9,
                "evidence_text": text[:200], # excerpt
                "page_number": page_number
            })
            
    for material in MANUFACTURING_MATERIALS:
        if material in text_lower:
            entities.append({
                "label": material,
                "entity_type": "Material",
                "confidence": 0.9,
                "evidence_text": text[:200],
                "page_number": page_number
            })
            
    for tool in MANUFACTURING_TOOLS:
        if tool in text_lower:
            entities.append({
                "label": tool,
                "entity_type": "Tool",
                "confidence": 0.9,
                "evidence_text": text[:200],
                "page_number": page_number
            })
            
    for sensor in MANUFACTURING_SENSORS:
        if sensor in text_lower:
            entities.append({
                "label": sensor,
                "entity_type": "Sensor",
                "confidence": 0.9,
                "evidence_text": text[:200],
                "page_number": page_number
            })

    for failure in MANUFACTURING_FAILURE_MODES:
        if failure in text_lower:
            entities.append({
                "label": failure,
                "entity_type": "FailureMode",
                "confidence": 0.9,
                "evidence_text": text[:200],
                "page_number": page_number
            })

    # 2. Measurement Extraction (Regex based)
    measurement_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*(degrees Celsius|kilowatt|kilowatt hour|millimetre|metre per second|newton|pascal|second|percentage|°C|kW|kWh|mm|m/s|N|Pa|s|%)', re.IGNORECASE)
    for match in measurement_pattern.finditer(text):
        val = match.group(1)
        unit = match.group(2)
        entities.append({
            "label": f"{val} {unit}",
            "entity_type": "Measurement",
            "confidence": 0.95,
            "evidence_text": text[max(0, match.start()-30):min(len(text), match.end()+30)],
            "page_number": page_number
        })

    return entities

def extract_relationships(entities: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
    # Very basic relation extraction based on co-occurrence in sentences.
    # In a real scenario, we'd use a Transformer model for relation extraction.
    relationships = []
    
    # Create an index of entities by type
    machines = [e for e in entities if e["entity_type"] == "Machine"]
    tools = [e for e in entities if e["entity_type"] == "Tool"]
    sensors = [e for e in entities if e["entity_type"] == "Sensor"]
    materials = [e for e in entities if e["entity_type"] == "Material"]
    processes = [e for e in entities if e["entity_type"] == "Process"]
    
    text_lower = text.lower()
    
    # "usesMachine" or "usesTool" (Process -> Machine/Tool)
    # E.g. "The CNC milling machine uses a carbide cutting tool." -> machine uses tool
    # Let's mock a simple relation: if machine and tool are in text, machine uses tool.
    for m in machines:
        for t in tools:
            relationships.append({
                "source_label": m["label"],
                "target_label": t["label"],
                "relation_type": "usesTool",
                "confidence": 0.7,
                "evidence_text": text[:200]
            })
            
    for s in sensors:
        for m in machines:
            relationships.append({
                "source_label": m["label"],
                "target_label": s["label"],
                "relation_type": "monitoredBy",
                "confidence": 0.8,
                "evidence_text": text[:200]
            })

    return relationships
