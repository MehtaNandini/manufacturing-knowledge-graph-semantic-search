import { useEffect, useState } from 'react';
import { fetchDocuments, fetchEntities } from '../services/api';

export default function Dashboard() {
  const [stats, setStats] = useState({ docs: 0, pending: 0, approved: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        const [docs, entities] = await Promise.all([
          fetchDocuments(),
          fetchEntities()
        ]);
        
        setStats({
          docs: docs.length,
          pending: entities.filter((e: any) => e.status === 'PENDING' || e.status === 'pending').length,
          approved: entities.filter((e: any) => e.status === 'APPROVED' || e.status === 'approved').length,
        });
      } catch (e) {
        console.error("Failed to load dashboard stats", e);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Platform overview and processing metrics.</p>
      </div>

      <div className="grid-cards">
        <div className="card">
          <h3 className="text-muted">Total Documents</h3>
          {loading ? <p>Loading...</p> : <h1 style={{ fontSize: '3rem', margin: '1rem 0' }}>{stats.docs}</h1>}
          <p className="text-muted" style={{ fontSize: '0.875rem' }}>Successfully ingested and processed</p>
        </div>
        
        <div className="card">
          <h3 className="text-muted">Pending Entities</h3>
          {loading ? <p>Loading...</p> : <h1 style={{ fontSize: '3rem', margin: '1rem 0', color: 'var(--warning)' }}>{stats.pending}</h1>}
          <p className="text-muted" style={{ fontSize: '0.875rem' }}>Awaiting human review</p>
        </div>

        <div className="card">
          <h3 className="text-muted">Knowledge Graph Nodes</h3>
          {loading ? <p>Loading...</p> : <h1 style={{ fontSize: '3rem', margin: '1rem 0', color: 'var(--success)' }}>{stats.approved}</h1>}
          <p className="text-muted" style={{ fontSize: '0.875rem' }}>Approved entities synced to RDF Store</p>
        </div>
      </div>
    </div>
  );
}
