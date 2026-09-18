import fs from 'fs';
import path from 'path';

const files = {
    'frontend/src/services/api.ts': import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/api'
});

export const getDashboardSummary = () => api.get('/dashboard/summary');
export const getAlerts = () => api.get('/alerts');
export const getAlertById = (id) => api.get(\/alerts/\\);
export const uploadPcap = (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/analyze/pcap', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
};
export default api;
,
    'frontend/src/App.tsx': import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Alerts from './pages/Alerts';
import AlertDetail from './pages/AlertDetail';
import PcapUpload from './pages/PcapUpload';
import { Activity, ShieldAlert, UploadCloud, Server } from 'lucide-react';
import './index.css';

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-slate-950 text-slate-100 font-sans">
        {/* Sidebar */}
        <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
          <div className="p-6 border-b border-slate-800">
            <h1 className="text-xl font-bold tracking-wider text-blue-500 flex items-center gap-2">
              <ShieldAlert /> SOC IDS
            </h1>
            <p className="text-xs text-slate-500 mt-1 uppercase tracking-widest">Unidirectional Threat Intel</p>
          </div>
          <nav className="flex-1 p-4 space-y-2">
            <Link to="/" className="flex items-center gap-3 p-3 rounded hover:bg-slate-800 transition">
              <Activity size={18} /> Dashboard
            </Link>
            <Link to="/alerts" className="flex items-center gap-3 p-3 rounded hover:bg-slate-800 transition">
              <ShieldAlert size={18} /> Alerts
            </Link>
            <Link to="/pcap" className="flex items-center gap-3 p-3 rounded hover:bg-slate-800 transition">
              <UploadCloud size={18} /> PCAP Analysis
            </Link>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/alerts/:id" element={<AlertDetail />} />
            <Route path="/pcap" element={<PcapUpload />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
,
    'frontend/tailwind.config.js': /** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
,
    'frontend/src/index.css': @tailwind base;
@tailwind components;
@tailwind utilities;

body {
  background-color: #020617; /* slate-950 */
  color: #f8fafc; /* slate-50 */
}

};

for (const [filePath, content] of Object.entries(files)) {
    const fullPath = path.resolve(filePath);
    fs.mkdirSync(path.dirname(fullPath), { recursive: true });
    fs.writeFileSync(fullPath, content);
}
console.log('Frontend setup complete.');
