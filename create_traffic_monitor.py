import os

files = {
    'frontend/src/pages/Traffic.tsx': '''import React, { useEffect, useState } from "react";
import api from "../services/api";
import { Activity } from "lucide-react";

export default function Traffic() {
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    api.get("/dashboard/summary").then(res => setSummary(res.data)).catch(console.error);
  }, []);

  if (!summary) return <div className="p-8 text-slate-400">Loading traffic analytics...</div>;

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <Activity /> Traffic Analytics
      </h2>
      <div className="bg-slate-900 border border-slate-800 p-6 rounded">
         <p className="text-slate-400 mb-4">Normalized Flow Statistics (Since startup)</p>
         <div className="grid grid-cols-2 gap-6">
           <div className="bg-slate-950 p-4 rounded border border-slate-800">
              <div className="text-sm text-slate-500 mb-1">Total Flows Analyzed</div>
              <div className="text-3xl font-bold text-blue-500">{summary.metrics.flows_analyzed}</div>
           </div>
           <div className="bg-slate-950 p-4 rounded border border-slate-800">
              <div className="text-sm text-slate-500 mb-1">Anomalies Detected</div>
              <div className="text-3xl font-bold text-yellow-500">{summary.metrics.anomalies_detected}</div>
           </div>
         </div>
      </div>
    </div>
  );
}
''',
    'frontend/src/pages/Monitor.tsx': '''import React, { useEffect, useState } from "react";
import api from "../services/api";
import { Radio } from "lucide-react";

export default function Monitor() {
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    const fetchLatest = () => {
       api.get("/alerts?limit=10").then(res => setAlerts(res.data)).catch(console.error);
    };
    fetchLatest();
    const intv = setInterval(fetchLatest, 3000);
    return () => clearInterval(intv);
  }, []);

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <Radio className="text-green-500 animate-pulse" /> Live Monitor Stream
      </h2>
      <div className="bg-slate-950 border border-slate-800 p-4 rounded h-96 overflow-y-auto font-mono text-sm">
         {alerts.length === 0 ? (
           <div className="text-slate-500 text-center mt-32">WAITING FOR TRAFFIC...</div>
         ) : (
           alerts.map((a, i) => (
             <div key={i} className="py-2 border-b border-slate-900 flex gap-4 hover:bg-slate-900 px-2">
               <span className="text-slate-500 w-48 shrink-0">{new Date(a.timestamp).toISOString()}</span>
               <span className="text-blue-400 w-16">{a.protocol}</span>
               <span className="text-slate-300 flex-1">{a.source_ip} &rarr; {a.destination_ip}</span>
               <span className={a.severity === 'CRITICAL' ? 'text-red-500 font-bold' : 'text-slate-400'}>{a.threat_type}</span>
             </div>
           ))
         )}
      </div>
    </div>
  );
}
''',
    'frontend/src/App.tsx': '''import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Alerts from "./pages/Alerts";
import AlertDetail from "./pages/AlertDetail";
import PcapUpload from "./pages/PcapUpload";
import Models from "./pages/Models";
import System from "./pages/System";
import Traffic from "./pages/Traffic";
import Monitor from "./pages/Monitor";
import { Activity, ShieldAlert, UploadCloud, BrainCircuit, Server, Radio, BarChart2 } from "lucide-react";
import "./index.css";

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-slate-950 text-slate-100 font-sans">
        <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
          <div className="p-6 border-b border-slate-800">
            <h1 className="text-xl font-bold tracking-wider text-blue-500 flex items-center gap-2">
              <ShieldAlert /> SOC IDS
            </h1>
            <p className="text-xs text-slate-500 mt-1 uppercase tracking-widest">Unidirectional Intel</p>
          </div>
          <nav className="flex-1 p-4 space-y-2">
            <Link to="/" className="flex items-center gap-3 p-3 rounded hover:bg-slate-800 transition">
              <Activity size={18} /> Dashboard
            </Link>
            <Link to="/monitor" className="flex items-center gap-3 p-3 rounded hover:bg-slate-800 transition">
              <Radio size={18} /> Live Monitor
            </Link>
            <Link to="/alerts" className="flex items-center gap-3 p-3 rounded hover:bg-slate-800 transition">
              <ShieldAlert size={18} /> Alerts
            </Link>
            <Link to="/traffic" className="flex items-center gap-3 p-3 rounded hover:bg-slate-800 transition">
              <BarChart2 size={18} /> Traffic Analytics
            </Link>
            <Link to="/pcap" className="flex items-center gap-3 p-3 rounded hover:bg-slate-800 transition">
              <UploadCloud size={18} /> PCAP Analysis
            </Link>
            <Link to="/models" className="flex items-center gap-3 p-3 rounded hover:bg-slate-800 transition">
              <BrainCircuit size={18} /> Models
            </Link>
            <Link to="/system" className="flex items-center gap-3 p-3 rounded hover:bg-slate-800 transition">
              <Server size={18} /> System Health
            </Link>
          </nav>
        </aside>
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/monitor" element={<Monitor />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/alerts/:id" element={<AlertDetail />} />
            <Route path="/traffic" element={<Traffic />} />
            <Route path="/pcap" element={<PcapUpload />} />
            <Route path="/models" element={<Models />} />
            <Route path="/system" element={<System />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
'''
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
