import { useState, useEffect } from 'react';
import { Check, X } from 'lucide-react';
import { fetchEntities, approveEntity, rejectEntity } from '../services/api';
import { ExtractedEntity } from '../types';

export default function Entities() {
  const [entities, setEntities] = useState<ExtractedEntity[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('pending');

  useEffect(() => {
    loadEntities();
  }, [filter]);

  const loadEntities = async () => {
    setLoading(true);
    try {
      const data = await fetchEntities(filter === 'all' ? undefined : filter);
      setEntities(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (id: string, action: 'approve' | 'reject') => {
    try {
      if (action === 'approve') await approveEntity(id);
      else await rejectEntity(id);
      loadEntities();
    } catch (e) {
      alert(`Failed to ${action} entity`);
    }
  };

  return (
    <div>
      <div className="page-header flex justify-between items-center">
        <div>
          <h1 className="page-title">Review Workflow</h1>
          <p className="page-subtitle">Human-in-the-loop review for NLP extraction before syncing to the Knowledge Graph.</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className={`btn ${filter === 'pending' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setFilter('pending')}>Pending</button>
          <button className={`btn ${filter === 'approved' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setFilter('approved')}>Approved</button>
          <button className={`btn ${filter === 'rejected' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setFilter('rejected')}>Rejected</button>
          <button className={`btn ${filter === 'all' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setFilter('all')}>All</button>
        </div>
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Label</th>
              <th>Type</th>
              <th>Confidence</th>
              <th>Evidence Text</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && <tr><td colSpan={6} className="text-center">Loading...</td></tr>}
            {!loading && entities.length === 0 && (
              <tr><td colSpan={6} className="text-center">No entities found for this filter.</td></tr>
            )}
            {entities.map((ent) => (
              <tr key={ent.id}>
                <td style={{ fontWeight: 600 }}>{ent.label}</td>
                <td><span className="badge badge-gray">{ent.entity_type}</span></td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ width: '50px', height: '6px', background: '#e2e8f0', borderRadius: '3px' }}>
                      <div style={{ width: `${ent.confidence * 100}%`, height: '100%', background: ent.confidence > 0.8 ? 'var(--success)' : 'var(--warning)', borderRadius: '3px' }}></div>
                    </div>
                    <span>{Math.round(ent.confidence * 100)}%</span>
                  </div>
                </td>
                <td style={{ maxWidth: '300px', fontSize: '0.875rem' }} className="text-muted">"{ent.evidence_text}"</td>
                <td>
                  <span className={`badge ${ent.status === 'approved' ? 'badge-green' : ent.status === 'rejected' ? 'badge-red' : 'badge-yellow'}`}>
                    {ent.status}
                  </span>
                </td>
                <td>
                  {ent.status === 'pending' && (
                    <div className="flex gap-2">
                      <button className="btn btn-success" onClick={() => handleAction(ent.id, 'approve')} title="Approve & Publish to KG"><Check size={16} /></button>
                      <button className="btn btn-danger" onClick={() => handleAction(ent.id, 'reject')} title="Reject"><X size={16} /></button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
