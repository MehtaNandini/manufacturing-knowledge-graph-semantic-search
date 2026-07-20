export interface User {
  id: number;
  email: string;
  role: string;
}

export interface Document {
  id: string;
  filename: string;
  content_type: string;
  file_size: number;
  status: string;
  uploaded_at: string;
}

export interface ExtractedEntity {
  id: string;
  document_id: string;
  label: string;
  entity_type: string;
  confidence: number;
  evidence_text?: string;
  page_number?: number;
  status: string;
  graph_uri?: string;
}

export interface SearchResult {
  text: string;
  score: number;
  document_id: string;
  page_number: number;
}
