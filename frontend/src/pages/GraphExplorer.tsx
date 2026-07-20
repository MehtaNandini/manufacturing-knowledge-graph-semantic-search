import { useEffect, useState } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import { fetchGraphSchema } from '../services/api';

export default function GraphExplorer() {
  const [elements, setElements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadGraph();
  }, []);

  const loadGraph = async () => {
    try {
      const result = await fetchGraphSchema();
      // result from fuseki usually is in { results: { bindings: [...] } } format
      const bindings = result.results?.bindings || [];
      
      const nodesMap = new Map();
      const edges: any[] = [];
      
      bindings.forEach((b: any) => {
        const s = b.s.value;
        const p = b.p.value;
        const o = b.o.value;

        // Add Subject Node
        if (!nodesMap.has(s)) {
          nodesMap.set(s, { data: { id: s, label: s.split('/').pop() || s } });
        }
        
        // Add Object Node if it's a URI
        if (b.o.type === 'uri') {
          if (!nodesMap.has(o)) {
            nodesMap.set(o, { data: { id: o, label: o.split('/').pop() || o } });
          }
          // Add Edge
          edges.push({ data: { source: s, target: o, label: p.split('#').pop()?.split('/').pop() || p } });
        } else {
          // It's a literal, add as node for viz purposes
          const literalId = `${s}_${p}_${o}`;
          nodesMap.set(literalId, { data: { id: literalId, label: o, type: 'literal' } });
          edges.push({ data: { source: s, target: literalId, label: p.split('#').pop()?.split('/').pop() || p } });
        }
      });

      setElements([...Array.from(nodesMap.values()), ...edges]);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const layout = {
    name: 'cose',
    idealEdgeLength: 100,
    nodeOverlap: 20,
    refresh: 20,
    fit: true,
    padding: 30,
    randomize: false,
    componentSpacing: 100,
    nodeRepulsion: 400000,
    edgeElasticity: 100,
    nestingFactor: 5,
    gravity: 80,
    numIter: 1000,
    initialTemp: 200,
    coolingFactor: 0.95,
    minTemp: 1.0
  };

  const stylesheet = [
    {
      selector: 'node',
      style: {
        'background-color': '#3b82f6',
        'label': 'data(label)',
        'color': '#1e293b',
        'font-size': '12px',
        'text-valign': 'bottom',
        'text-halign': 'center',
        'text-margin-y': '5px',
        'width': '30px',
        'height': '30px',
      }
    },
    {
      selector: 'node[type="literal"]',
      style: {
        'background-color': '#10b981',
        'shape': 'rectangle',
        'width': '60px',
        'height': '20px',
      }
    },
    {
      selector: 'edge',
      style: {
        'width': 2,
        'line-color': '#cbd5e1',
        'target-arrow-color': '#cbd5e1',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'label': 'data(label)',
        'font-size': '10px',
        'color': '#64748b',
        'text-rotation': 'autorotate',
        'text-margin-y': '-10px'
      }
    }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div className="page-header">
        <h1 className="page-title">Graph Explorer</h1>
        <p className="page-subtitle">Interactive visualization of the Manufacturing Knowledge Graph.</p>
      </div>

      <div className="card" style={{ flex: 1, padding: 0, overflow: 'hidden', minHeight: '600px' }}>
        {loading ? (
          <div style={{ padding: '2rem', textAlign: 'center' }}>Loading graph data...</div>
        ) : (
          elements.length > 0 ? (
            <CytoscapeComponent 
              elements={elements} 
              style={{ width: '100%', height: '100%' }} 
              layout={layout}
              stylesheet={stylesheet}
            />
          ) : (
            <div style={{ padding: '2rem', textAlign: 'center' }}>No approved knowledge graph nodes found. Review some entities first!</div>
          )
        )}
      </div>
    </div>
  );
}
