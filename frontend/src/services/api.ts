import axios from 'axios';
import { Document, ExtractedEntity, SearchResult } from '../types';

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const fetchDocuments = async (): Promise<Document[]> => {
  const { data } = await api.get('/api/documents/');
  return data;
};

export const uploadDocument = async (file: File): Promise<Document> => {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/api/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return data;
};

export const fetchEntities = async (status?: string): Promise<ExtractedEntity[]> => {
  const url = status ? `/api/entities/?status=${status}` : '/api/entities/';
  const { data } = await api.get(url);
  return data;
};

export const approveEntity = async (id: string): Promise<ExtractedEntity> => {
  const { data } = await api.post(`/api/entities/${id}/approve`);
  return data;
};

export const rejectEntity = async (id: string): Promise<ExtractedEntity> => {
  const { data } = await api.post(`/api/entities/${id}/reject`);
  return data;
};

export const semanticSearch = async (query: string): Promise<SearchResult[]> => {
  const { data } = await api.post('/api/search/semantic', { query, limit: 10 });
  return data;
};

export const sparqlQuery = async (query: string): Promise<any> => {
  const { data } = await api.post('/api/graph/query', { query });
  return data;
};

export const fetchGraphSchema = async (): Promise<any> => {
  // Simplified wrapper for graph visualisation
  const query = `
    PREFIX mfg: <http://example.org/manufacturing/>
    SELECT ?s ?p ?o
    WHERE {
      ?s ?p ?o .
      FILTER(?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>)
    }
    LIMIT 200
  `;
  const { data } = await api.post('/api/graph/query', { query });
  return data;
};
