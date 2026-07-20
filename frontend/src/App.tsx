import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { Database, FileText, Search, Activity, Network } from 'lucide-react';
import './index.css';

import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Entities from './pages/Entities';
import GraphExplorer from './pages/GraphExplorer';
import SemanticSearch from './pages/SemanticSearch';

function App() {
  return (
    <Router>
      <div className="app-container">
        <nav className="sidebar">
          <div className="sidebar-title">
            <Database size={24} color="#3b82f6" />
            <span>Mfg KG Platform</span>
          </div>
          
          <ul className="nav-menu">
            <li>
              <NavLink to="/" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
                <Activity size={20} />
                Dashboard
              </NavLink>
            </li>
            <li>
              <NavLink to="/documents" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
                <FileText size={20} />
                Documents
              </NavLink>
            </li>
            <li>
              <NavLink to="/entities" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
                <Database size={20} />
                Review Workflow
              </NavLink>
            </li>
            <li>
              <NavLink to="/graph" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
                <Network size={20} />
                Graph Explorer
              </NavLink>
            </li>
            <li>
              <NavLink to="/search" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
                <Search size={20} />
                Semantic Search
              </NavLink>
            </li>
          </ul>
        </nav>
        
        <main className="main-content">
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
