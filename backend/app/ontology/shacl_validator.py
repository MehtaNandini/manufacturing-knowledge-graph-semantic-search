from pyshacl import validate
from rdflib import Graph
import os

def validate_graph(data_graph: Graph) -> dict:
    """
    Validates a data graph against the manufacturing SHACL shapes.
    """
    shapes_file = os.path.join(os.path.dirname(__file__), "../../../ontology/manufacturing_shapes.ttl")
    shapes_graph = Graph()
    shapes_graph.parse(shapes_file, format="turtle")
    
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False,
        meta_shacl=False,
        debug=False
    )
    
    return {
        "conforms": conforms,
        "results_text": results_text
    }
