
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './index.css';

// Minimal mock pages for scaffold
const Dashboard = () => (
  <div style={{ padding: '20px' }}>
    <h2>Dashboard</h2>
    <p>Welcome to the Manufacturing Knowledge Graph</p>
  </div>
);
const Documents = () => <div style={{ padding: '20px' }}><h2>Documents</h2></div>;
const Entities = () => <div style={{ padding: '20px' }}><h2>Entities</h2></div>;
const GraphExplorer = () => <div style={{ padding: '20px' }}><h2>Graph Explorer</h2></div>;
const SemanticSearch = () => <div style={{ padding: '20px' }}><h2>Semantic Search</h2></div>;

function App() {
  return (
    <Router>
      <div style={{ display: 'flex', minHeight: '100vh', fontFamily: 'sans-serif' }}>
        <nav style={{ width: '250px', background: '#1e293b', color: 'white', padding: '20px' }}>
          <h1 style={{ fontSize: '1.2rem', marginBottom: '2rem' }}>Mfg KG Platform</h1>
          <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <li><Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Dashboard</Link></li>
            <li><Link to="/documents" style={{ color: 'white', textDecoration: 'none' }}>Documents</Link></li>
            <li><Link to="/entities" style={{ color: 'white', textDecoration: 'none' }}>Review Workflow</Link></li>
            <li><Link to="/graph" style={{ color: 'white', textDecoration: 'none' }}>Graph Explorer</Link></li>
            <li><Link to="/search" style={{ color: 'white', textDecoration: 'none' }}>Semantic Search</Link></li>
          </ul>
        </nav>
        <main style={{ flex: 1, background: '#f8fafc' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/entities" element={<Entities />} />
            <Route path="/graph" element={<GraphExplorer />} />
            <Route path="/search" element={<SemanticSearch />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
