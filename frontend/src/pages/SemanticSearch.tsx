import { useState } from 'react';
import { Search } from 'lucide-react';
import { semanticSearch, sparqlQuery } from '../services/api';

export default function SemanticSearch() {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState<'semantic' | 'sparql'>('semantic');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setResults([]);
    try {
      if (mode === 'semantic') {
        const data = await semanticSearch(query);
        setResults(data);
      } else {
        const data = await sparqlQuery(query);
        // Map SPARQL results to generic array for display
        const bindings = data.results?.bindings || [];
        setResults(bindings);
      }
    } catch (err) {
      alert("Search failed. Check your query syntax.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Search Workspace</h1>
        <p className="page-subtitle">Find documents via hybrid vector search, or query the graph directly via SPARQL.</p>
      </div>

      <div className="card" style={{ marginBottom: '2rem' }}>
        <div className="flex gap-4 mb-4">
          <button 
            className={`btn ${mode === 'semantic' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => { setMode('semantic'); setResults([]); }}
          >
            Hybrid Semantic Search
          </button>
          <button 
            className={`btn ${mode === 'sparql' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => { 
              setMode('sparql'); 
              setQuery('PREFIX mfg: <http://example.org/manufacturing/>\nSELECT ?s ?p ?o\nWHERE { ?s ?p ?o }\nLIMIT 10');
              setResults([]); 
            }}
          >
            SPARQL Workbench
          </button>
        </div>

        <form onSubmit={handleSearch} className="flex gap-4">
          {mode === 'semantic' ? (
            <input 
              type="text" 
              className="input input-large" 
              placeholder="e.g. Which machine caused the overheating defect?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{ flex: 1 }}
            />
          ) : (
            <textarea
              className="input"
              rows={5}
              style={{ flex: 1, fontFamily: 'monospace' }}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          )}
          <button type="submit" className="btn btn-primary" style={{ padding: '0 2rem' }} disabled={loading}>
            <Search size={20} />
            {loading ? "Searching..." : "Search"}
          </button>
        </form>
      </div>

      {results.length > 0 && (
        <div>
          <h3>Results ({results.length})</h3>
          
          {mode === 'semantic' ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
              {results.map((res, idx) => (
                <div key={idx} className="card" style={{ marginBottom: 0 }}>
                  <div className="flex justify-between items-center mb-2">
                    <span className="badge badge-blue">Doc ID: {res.document_id} (Page {res.page_number})</span>
                    <span className="text-muted">Relevance Score: {res.score.toFixed(3)}</span>
                  </div>
                  <p>"{res.text}"</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="table-container mt-4">
              <table>
                <thead>
                  <tr>
                    {Object.keys(results[0] || {}).map(key => <th key={key}>{key}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {results.map((row, idx) => (
                    <tr key={idx}>
                      {Object.values(row).map((val: any, vIdx) => (
                        <td key={vIdx}>{val.value}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
      
      {!loading && query && results.length === 0 && (
        <div className="text-center text-muted mt-4">
          Press Search to find results.
        </div>
      )}
    </div>
  );
}
