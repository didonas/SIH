import os

files = {
    'frontend/src/App.tsx': '''import React from "react";
import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom";
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
  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    lex items-center gap-3 p-3 rounded transition-colors text-sm font-medium ;

  return (
    <Router>
      <div className="flex h-screen bg-slate-950 text-slate-100 font-sans selection:bg-blue-500/30">
        <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shadow-2xl z-10">
          <div className="p-6 border-b border-slate-800 bg-slate-900/50">
            <h1 className="text-xl font-bold tracking-wider text-blue-500 flex items-center gap-3">
              <ShieldAlert className="text-blue-500" /> SOC IDS
            </h1>
            <p className="text-[10px] text-slate-500 mt-2 uppercase tracking-widest font-semibold">
              Unidirectional Intel
            </p>
          </div>
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            <div className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2 ml-3 mt-2">Analysis</div>
            <NavLink to="/" className={navLinkClass}>
              <Activity size={18} /> Dashboard
            </NavLink>
            <NavLink to="/monitor" className={navLinkClass}>
              <Radio size={18} /> Live Monitor
            </NavLink>
            <NavLink to="/traffic" className={navLinkClass}>
              <BarChart2 size={18} /> Traffic Analytics
            </NavLink>
            
            <div className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2 ml-3 mt-6">Detection</div>
            <NavLink to="/alerts" className={navLinkClass}>
              <ShieldAlert size={18} /> Alerts
            </NavLink>
            <NavLink to="/models" className={navLinkClass}>
              <BrainCircuit size={18} /> Models
            </NavLink>

            <div className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2 ml-3 mt-6">Ingestion</div>
            <NavLink to="/pcap" className={navLinkClass}>
              <UploadCloud size={18} /> PCAP Analysis
            </NavLink>
            
            <div className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2 ml-3 mt-6">System</div>
            <NavLink to="/system" className={navLinkClass}>
              <Server size={18} /> System Health
            </NavLink>
          </nav>
        </aside>
        <main className="flex-1 overflow-y-auto bg-slate-950">
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
''',
    'frontend/src/pages/Dashboard.tsx': '''import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import { Activity, ShieldAlert, Cpu, Database, Network } from "lucide-react";

export default function Dashboard() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    api.get("/dashboard/summary").then(res => setData(res.data)).catch(console.error);
  }, []);

  if (!data) return <div className="p-8 text-slate-400 font-mono animate-pulse">Initializing dashboard...</div>;

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <header className="mb-8">
        <h2 className="text-3xl font-bold tracking-tight mb-2">SOC Overview</h2>
        <p className="text-slate-400 text-sm">Real-time threat intelligence and unidirectional traffic analysis.</p>
      </header>
      
      {/* System Status Row */}
      <div className="grid grid-cols-5 gap-4 mb-8">
        {[
          { label: "Detection Engine", val: data.status.detection_engine, icon: <Cpu size={16}/> },
          { label: "Zeek Adapter", val: data.status.zeek, icon: <Network size={16}/> },
          { label: "ML Pipeline", val: data.status.ml_model, icon: <Activity size={16}/> },
          { label: "Database", val: data.status.database, icon: <Database size={16}/> },
          { label: "Traffic Input", val: data.status.traffic_input, icon: <Network size={16}/> },
        ].map(item => (
          <div key={item.label} className="bg-slate-900 p-4 rounded-lg border border-slate-800 shadow-sm">
            <div className="flex items-center gap-2 text-xs text-slate-500 font-semibold uppercase tracking-wider mb-2">
              {item.icon} {item.label}
            </div>
            <div className={	ext-sm font-bold }>
              {item.val}
            </div>
          </div>
        ))}
      </div>

      {/* Threat Metrics */}
      <h3 className="text-lg font-semibold mb-4 text-slate-300">Analysis Metrics</h3>
      <div className="grid grid-cols-4 gap-6 mb-8">
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-md">
          <div className="text-sm text-slate-400 font-medium mb-1">Flows Analyzed</div>
          <div className="text-4xl font-black text-blue-500">{data.metrics.flows_analyzed.toLocaleString()}</div>
        </div>
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-md">
          <div className="text-sm text-slate-400 font-medium mb-1">Threats Detected</div>
          <div className="text-4xl font-black text-red-500">{data.metrics.threats_detected.toLocaleString()}</div>
        </div>
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-md col-span-2">
           <div className="text-sm text-slate-400 font-medium mb-4">Severity Distribution</div>
           <div className="flex gap-4">
              <div className="flex-1 bg-slate-950 p-3 rounded-lg border border-slate-800 flex items-center justify-between">
                 <span className="text-xs font-bold text-red-500">CRITICAL</span>
                 <span className="font-mono">{data.metrics.critical_alerts}</span>
              </div>
              <div className="flex-1 bg-slate-950 p-3 rounded-lg border border-slate-800 flex items-center justify-between">
                 <span className="text-xs font-bold text-orange-500">HIGH</span>
                 <span className="font-mono">{data.metrics.high_alerts}</span>
              </div>
              <div className="flex-1 bg-slate-950 p-3 rounded-lg border border-slate-800 flex items-center justify-between">
                 <span className="text-xs font-bold text-yellow-500">MEDIUM</span>
                 <span className="font-mono">{data.metrics.medium_alerts}</span>
              </div>
           </div>
        </div>
      </div>

      {/* Quick Action */}
      <div className="flex justify-end">
        <Link to="/alerts" className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center gap-2">
           <ShieldAlert size={16} /> View All Alerts
        </Link>
      </div>
    </div>
  );
}
''',
    'frontend/src/pages/Alerts.tsx': '''import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAlerts } from "../services/api";
import { ShieldAlert, Search } from "lucide-react";

export default function Alerts() {
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    getAlerts().then(res => setAlerts(res.data)).catch(console.error);
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-end mb-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight flex items-center gap-3 mb-2">
            <ShieldAlert className="text-red-500" /> Threat Alerts
          </h2>
          <p className="text-slate-400 text-sm">Detected anomalies and matched signatures.</p>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-2.5 text-slate-500" size={16} />
          <input type="text" placeholder="Filter alerts..." className="bg-slate-900 border border-slate-700 text-sm rounded-lg pl-9 pr-4 py-2 text-slate-200 focus:outline-none focus:border-blue-500 transition-colors" />
        </div>
      </div>
      
      {alerts.length === 0 ? (
        <div className="bg-slate-900/50 p-16 flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-700 text-slate-400">
           <ShieldAlert size={48} className="mb-4 text-slate-600" />
           <p className="font-semibold text-lg">No Alerts Detected</p>
           <p className="text-sm mt-1">The system has not registered any threats based on current analysis.</p>
        </div>
      ) : (
        <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left whitespace-nowrap">
              <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-4 font-semibold">Time</th>
                  <th className="px-6 py-4 font-semibold">Source</th>
                  <th className="px-6 py-4 font-semibold">Destination</th>
                  <th className="px-6 py-4 font-semibold">Threat Type</th>
                  <th className="px-6 py-4 font-semibold">Severity</th>
                  <th className="px-6 py-4 font-semibold">Risk</th>
                  <th className="px-6 py-4 font-semibold">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {alerts.map(a => (
                  <tr key={a.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 text-sm text-slate-300 font-mono">{new Date(a.timestamp).toLocaleString()}</td>
                    <td className="px-6 py-4 text-sm font-mono text-slate-300">{a.source_ip}:{a.source_port}</td>
                    <td className="px-6 py-4 text-sm font-mono text-slate-300">{a.destination_ip}:{a.destination_port}</td>
                    <td className="px-6 py-4 text-sm font-semibold text-slate-200">{a.threat_type}</td>
                    <td className="px-6 py-4">
                      <span className={px-2.5 py-1 text-[10px] uppercase tracking-wider rounded-md font-bold border }>
                        {a.severity}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm font-mono">
                      <span className={a.risk_score >= 80 ? 'text-red-400 font-bold' : 'text-slate-300'}>{a.risk_score}</span>
                    </td>
                    <td className="px-6 py-4">
                      <Link to={/alerts/} className="text-blue-400 hover:text-blue-300 font-medium text-sm transition-colors">Investigate &rarr;</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
''',
    'frontend/src/pages/AlertDetail.tsx': '''import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getAlertById } from "../services/api";
import { ArrowLeft, ShieldAlert, Target, Activity, FileText } from "lucide-react";

export default function AlertDetail() {
  const { id } = useParams<{ id: string }>();
  const [alert, setAlert] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      getAlertById(id)
        .then(res => setAlert(res.data))
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [id]);

  if (loading) return <div className="p-8 text-slate-400 font-mono animate-pulse">Loading investigation data...</div>;
  if (!alert) return <div className="p-8 text-red-400">Alert not found.</div>;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-6">
        <Link to="/alerts" className="text-slate-400 hover:text-slate-200 text-sm flex items-center gap-2 w-fit mb-4 transition-colors">
          <ArrowLeft size={16} /> Back to Alerts
        </Link>
        <h2 className="text-3xl font-bold tracking-tight text-slate-100">Investigation: #{alert.id}</h2>
        <p className="text-slate-400 mt-1 font-mono text-sm">{new Date(alert.timestamp).toISOString()}</p>
      </div>

      <div className="grid grid-cols-3 gap-6 mb-8">
        {/* Core details */}
        <div className="col-span-2 bg-slate-900 rounded-xl border border-slate-800 shadow-xl overflow-hidden">
          <div className="bg-slate-950 p-4 border-b border-slate-800 flex items-center gap-2">
            <Target size={18} className="text-slate-400" /> 
            <h3 className="font-semibold text-slate-200">Connection Details</h3>
          </div>
          <div className="p-6 grid grid-cols-2 gap-8">
            <div>
              <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Source</div>
              <div className="text-lg font-mono text-slate-200">{alert.source_ip}:{alert.source_port}</div>
            </div>
            <div>
              <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Destination</div>
              <div className="text-lg font-mono text-slate-200">{alert.destination_ip}:{alert.destination_port}</div>
            </div>
            <div>
              <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Protocol</div>
              <div className="text-lg font-mono text-slate-200">{alert.protocol}</div>
            </div>
            <div>
              <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Threat Type</div>
              <div className="text-lg font-bold text-red-400">{alert.threat_type}</div>
            </div>
          </div>
        </div>

        {/* Scoring */}
        <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-xl overflow-hidden flex flex-col">
          <div className="bg-slate-950 p-4 border-b border-slate-800 flex items-center gap-2">
            <Activity size={18} className="text-slate-400" />
            <h3 className="font-semibold text-slate-200">Risk Assessment</h3>
          </div>
          <div className="p-6 flex-1 flex flex-col justify-center space-y-6">
            <div>
              <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Severity</div>
              <span className={px-3 py-1 text-xs rounded-md font-bold uppercase tracking-wider border }>
                {alert.severity}
              </span>
            </div>
            <div>
              <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Calculated Risk Score</div>
              <div className="text-4xl font-black text-slate-100">{alert.risk_score}<span className="text-lg text-slate-500 font-normal">/100</span></div>
            </div>
            <div>
              <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Model Inference</div>
              <div className="text-sm text-slate-300 font-mono">{alert.model_used}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Evidence */}
      <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-xl overflow-hidden">
         <div className="bg-slate-950 p-4 border-b border-slate-800 flex items-center gap-2">
            <FileText size={18} className="text-slate-400" />
            <h3 className="font-semibold text-slate-200">Why was this detected?</h3>
         </div>
         <div className="p-6">
            <p className="text-sm text-slate-400 mb-4">The following factual indicators and model scores contributed to this alert:</p>
            <ul className="space-y-3">
              {Array.isArray(alert.evidence) && alert.evidence.length > 0 ? (
                alert.evidence.map((ev: string, i: number) => (
                  <li key={i} className="flex items-start gap-3 p-3 bg-slate-950/50 rounded-lg border border-slate-800/50">
                    <ShieldAlert size={16} className="text-blue-500 mt-0.5 shrink-0" />
                    <span className="font-mono text-sm text-slate-300">{ev}</span>
                  </li>
                ))
              ) : (
                <li className="text-slate-500 italic text-sm">No specific evidence attached.</li>
              )}
            </ul>
         </div>
      </div>
    </div>
  );
}
'''
}

for path, content in files.items():
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
