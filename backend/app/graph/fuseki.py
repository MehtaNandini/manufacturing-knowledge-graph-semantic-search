import os
from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET
from rdflib import Graph
import httpx

FUSEKI_URL = os.getenv("FUSEKI_URL", "http://localhost:3030/manufacturing")
FUSEKI_UPDATE_URL = f"{FUSEKI_URL}/update"
FUSEKI_QUERY_URL = f"{FUSEKI_URL}/query"
FUSEKI_DATA_URL = f"{FUSEKI_URL}/data"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

class FusekiClient:
    def __init__(self):
        self.query_wrapper = SPARQLWrapper(FUSEKI_QUERY_URL)
        self.query_wrapper.setReturnFormat(JSON)
        
        self.update_wrapper = SPARQLWrapper(FUSEKI_UPDATE_URL)
        self.update_wrapper.setMethod(POST)
        self.update_wrapper.setCredentials("admin", ADMIN_PASSWORD)

    def query(self, query_str: str) -> dict:
        self.query_wrapper.setQuery(query_str)
        try:
            return self.query_wrapper.queryAndConvert()
        except Exception as e:
            raise Exception(f"SPARQL Query failed: {str(e)}")

    def update(self, update_str: str):
        self.update_wrapper.setQuery(update_str)
        try:
            self.update_wrapper.query()
        except Exception as e:
            raise Exception(f"SPARQL Update failed: {str(e)}")

    def insert_graph(self, graph: Graph):
        # Insert rdflib Graph into Fuseki
        ntriples = graph.serialize(format="nt")
        if not ntriples:
            return
        # Use SPARQL UPDATE to insert data
        update_query = f"INSERT DATA {{ {ntriples} }}"
        self.update(update_query)
            
    def get_statistics(self):
        query = """
        SELECT ?class (COUNT(?s) AS ?count)
        WHERE {
          ?s a ?class .
        } GROUP BY ?class
        """
        return self.query(query)

fuseki_client = FusekiClient()
