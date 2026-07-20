# Architecture

## System Components

1.  **Frontend (React/Vite)**
    *   Provides user interfaces for uploading documents, reviewing extractions, and searching.
    *   Communicates with the backend via REST API.

2.  **Backend (FastAPI)**
    *   **Auth Module:** Manages JWT creation and role-based access control.
    *   **Ingestion Pipeline:** Validates files, chunks text, and coordinates extraction.
    *   **NLP Pipeline:** Uses SpaCy and regular expressions to extract domain entities and relations.
    *   **Graph Module:** Connects to Jena Fuseki via `SPARQLWrapper` and `httpx`.
    *   **Search Module:** Connects to Qdrant via `qdrant-client` to perform hybrid search.

3.  **PostgreSQL (Relational Database)**
    *   Stores users, documents, document chunks, and pending/approved entities and relationships.
    *   Serves as the primary source of truth before knowledge is published to the graph.

4.  **Apache Jena Fuseki (Triple Store)**
    *   Stores the RDF knowledge graph.
    *   Executes SPARQL queries.

5.  **Qdrant (Vector Database)**
    *   Stores sentence embeddings for text chunks to enable semantic search.

## Data Flow (Ingestion to Search)

1. User uploads document (Frontend -> Backend).
2. Backend saves file, extracts text, chunks text.
3. NLP pipeline extracts pending entities/relations.
4. User reviews and approves entities (Frontend -> Backend).
5. Approved entities are serialized to RDF and inserted into Jena Fuseki.
6. Vector embeddings for chunks are generated and inserted into Qdrant.
7. User searches (Hybrid): Backend queries Qdrant and Fuseki, combines results, and returns citations.
