import os

files = {
    'frontend/src/pages/Models.tsx': '''import React, { useEffect, useState } from "react";
import api from "../services/api";
import { BrainCircuit, CheckCircle, XCircle } from "lucide-react";

export default function Models() {
  const [models, setModels] = useState<any[]>([]);

  useEffect(() => {
    api.get("/models").then(res => setModels(res.data)).catch(console.error);
  }, []);

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <BrainCircuit /> Detection Models
      </h2>
      
      <div className="grid grid-cols-2 gap-8">
        {models.map(m => (
          <div key={m.name} className="bg-slate-900 border border-slate-800 rounded p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold text-blue-400">{m.name}</h3>
                <p className="text-sm text-slate-400">{m.algorithm}</p>
              </div>
              {m.status === "LOADED" ? 
                <CheckCircle className="text-green-500" /> : 
                <XCircle className="text-red-500" />
              }
            </div>
            
            <div className="space-y-2 text-sm text-slate-300 mb-6">
              <div className="flex justify-between border-b border-slate-800 pb-1">
                <span>Status</span>
                <span className={m.status === "LOADED" ? "text-green-500" : "text-red-500"}>{m.status}</span>
              </div>
              <div className="flex justify-between border-b border-slate-800 pb-1">
                <span>Version</span>
                <span>{m.version}</span>
              </div>
              <div className="flex justify-between border-b border-slate-800 pb-1">
                <span>Features Used</span>
                <span>{m.features}</span>
              </div>
            </div>

            {m.metrics && (
              <div>
                <h4 className="text-sm font-semibold text-slate-400 mb-3 uppercase tracking-wider">Evaluation Metrics (Test Data)</h4>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(m.metrics).map(([k, v]) => (
                    <div key={k} className="bg-slate-950 p-3 rounded border border-slate-800">
                      <div className="text-xs text-slate-500 capitalize">{k.replace('_', ' ')}</div>
                      <div className="text-lg font-bold">{String(v)}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
''',
    'frontend/src/pages/System.tsx': '''import React, { useEffect, useState } from "react";
import api from "../services/api";
import { Server, Cpu, HardDrive } from "lucide-react";

export default function System() {
  const [sys, setSys] = useState<any>(null);

  useEffect(() => {
    const fetchSys = () => {
      api.get("/system").then(res => setSys(res.data)).catch(console.error);
    };
    fetchSys();
    const intv = setInterval(fetchSys, 5000);
    return () => clearInterval(intv);
  }, []);

  if (!sys) return <div className="p-8 text-slate-400">Loading system health...</div>;

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <Server /> System Health
      </h2>
      
      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded flex items-center gap-4">
           <Cpu className="text-blue-500" size={32} />
           <div>
             <div className="text-sm text-slate-400">CPU Usage</div>
             <div className="text-2xl font-bold">{sys.cpu_usage_percent}%</div>
           </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded flex items-center gap-4">
           <HardDrive className="text-purple-500" size={32} />
           <div>
             <div className="text-sm text-slate-400">Memory Usage</div>
             <div className="text-2xl font-bold">{sys.memory_usage_percent}%</div>
           </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded flex items-center gap-4">
           <Server className="text-green-500" size={32} />
           <div>
             <div className="text-sm text-slate-400">Uptime</div>
             <div className="text-2xl font-bold">{sys.uptime_seconds}s</div>
           </div>
        </div>
      </div>

      <h3 className="text-lg font-semibold mb-4 border-b border-slate-800 pb-2">Component Status</h3>
      <div className="bg-slate-900 rounded border border-slate-800 overflow-hidden">
        <table className="w-full text-left">
          <tbody>
            {Object.entries(sys.components).map(([k, v]) => (
              <tr key={k} className="border-b border-slate-800 last:border-0">
                <td className="p-4 capitalize font-medium">{k.replace('_', ' ')}</td>
                <td className="p-4">
                  <span className={px-2 py-1 text-xs rounded font-bold }>
                    {String(v)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
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
import { Activity, ShieldAlert, UploadCloud, BrainCircuit, Server } from "lucide-react";
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
            <Link to="/alerts" className="flex items-center gap-3 p-3 rounded hover:bg-slate-800 transition">
              <ShieldAlert size={18} /> Alerts
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
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/alerts/:id" element={<AlertDetail />} />
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
