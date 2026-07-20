import pytest
from app.extraction.nlp_pipeline import extract_entities, extract_relationships

def test_machine_tool_extraction():
    # TC UNIT 008
    text = "The CNC milling machine uses a carbide cutting tool."
    entities = extract_entities(text)
    labels = [e["label"] for e in entities]
    assert "cnc milling machine" in labels
    assert "carbide cutting tool" in labels

def test_material_extraction():
    # TC UNIT 009
    text = "The welding process consumes stainless steel."
    entities = extract_entities(text)
    labels = [e["label"] for e in entities]
    assert "stainless steel" in labels
    assert "welding" in labels # Process
    
def test_measurement_extraction():
    # TC UNIT 011
    text = "The motor temperature reached 85 degrees Celsius."
    entities = extract_entities(text)
    measurements = [e for e in entities if e["entity_type"] == "Measurement"]
    assert len(measurements) > 0
    assert "85 degrees Celsius" in [m["label"] for m in measurements]
