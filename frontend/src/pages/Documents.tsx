import { useState, useEffect, useRef } from 'react';
import { UploadCloud } from 'lucide-react';
import { fetchDocuments, uploadDocument, deleteDocument } from '../services/api';
import type { Document } from '../types';

export default function Documents() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const data = await fetchDocuments();
      setDocuments(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Are you sure you want to delete this document?")) return;
    try {
      await deleteDocument(id);
      await loadDocuments();
    } catch (err) {
      alert("Failed to delete document.");
    }
  };

  const handleFileDrop = async (e: any) => {
    e.preventDefault();
    const file = e.dataTransfer?.files[0] || e.target?.files[0];
    if (!file) return;

    setUploading(true);
    try {
      await uploadDocument(file);
      await loadDocuments();
    } catch (err: any) {
      if (err.response?.status === 409) {
        alert("A document with this filename already exists. Please delete it first or rename the file.");
      } else {
        alert("Failed to upload document");
      }
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Documents</h1>
        <p className="page-subtitle">Upload and manage manufacturing logs and manuals.</p>
      </div>

      <div 
        className="upload-area" 
        style={{ marginBottom: '2rem' }}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleFileDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <UploadCloud className="upload-icon" />
        <div>
          <h3>{uploading ? "Processing Document..." : "Click or drag file to this area to upload"}</h3>
          <p className="text-muted">Supports PDF, DOCX, TXT, and HTML files.</p>
        </div>
        <input 
          type="file" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          onChange={handleFileDrop}
          accept=".pdf,.docx,.txt,.html"
        />
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Filename</th>
              <th>Type</th>
              <th>Size</th>
              <th>Status</th>
              <th>Uploaded At</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && <tr><td colSpan={6} className="text-center">Loading documents...</td></tr>}
            {!loading && documents.length === 0 && (
              <tr><td colSpan={6} className="text-center">No documents uploaded yet.</td></tr>
            )}
            {documents.map((doc) => (
              <tr key={doc.id}>
                <td style={{ fontWeight: 500 }}>{doc.filename}</td>
                <td>{doc.content_type}</td>
                <td>{(doc.file_size / 1024).toFixed(1)} KB</td>
                <td>
                  <span className={`badge ${doc.status === 'processed' ? 'badge-green' : 'badge-yellow'}`}>
                    {doc.status}
                  </span>
                </td>
                <td>{new Date(doc.uploaded_at).toLocaleString()}</td>
                <td>
                  <button 
                    className="btn btn-outline" 
                    style={{ padding: '0.25rem 0.5rem', color: '#e74c3c', borderColor: '#e74c3c' }}
                    onClick={() => handleDelete(doc.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
