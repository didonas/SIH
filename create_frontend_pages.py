import os

files = {
    'frontend/tailwind.config.js': '''/** @type {import('tailwindcss').Config} */
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
''',
    'frontend/postcss.config.js': '''export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
''',
    'frontend/src/index.css': '''@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  background-color: #020617;
  color: #f8fafc;
}
''',
    'frontend/src/services/api.ts': '''import axios from "axios";

const api = axios.create({
    baseURL: "http://localhost:8000/api"
});

export const getDashboardSummary = () => api.get("/dashboard/summary");
export const getAlerts = () => api.get("/alerts");
export const getAlertById = (id: string) => api.get(/alerts/);
export const uploadPcap = (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/analyze/pcap", formData, {
        headers: { "Content-Type": "multipart/form-data" }
    });
};
export default api;
''',
    'frontend/src/App.tsx': '''import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Alerts from "./pages/Alerts";
import AlertDetail from "./pages/AlertDetail";
import PcapUpload from "./pages/PcapUpload";
import { Activity, ShieldAlert, UploadCloud } from "lucide-react";
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
''',
    'frontend/src/pages/Dashboard.tsx': '''import React, { useEffect, useState } from "react";
import { getDashboardSummary } from "../services/api";
import { Activity, Server, AlertTriangle } from "lucide-react";

export default function Dashboard() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    getDashboardSummary().then(res => setData(res.data)).catch(console.error);
  }, []);

  if (!data) return <div className="p-8 text-slate-400">Loading dashboard...</div>;

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6">Security Operations Overview</h2>
      
      <div className="grid grid-cols-4 gap-6 mb-8">
        <div className="bg-slate-900 p-6 rounded border border-slate-800">
          <h3 className="text-sm text-slate-400 mb-2">Detection Engine</h3>
          <p className={	ext-xl font-bold }>{data.status.detection_engine}</p>
        </div>
        <div className="bg-slate-900 p-6 rounded border border-slate-800">
          <h3 className="text-sm text-slate-400 mb-2">Zeek Adapter</h3>
          <p className="text-xl font-bold text-yellow-500">{data.status.zeek}</p>
        </div>
        <div className="bg-slate-900 p-6 rounded border border-slate-800">
          <h3 className="text-sm text-slate-400 mb-2">ML Model</h3>
          <p className="text-xl font-bold text-blue-500">{data.status.ml_model}</p>
        </div>
        <div className="bg-slate-900 p-6 rounded border border-slate-800">
          <h3 className="text-sm text-slate-400 mb-2">Database</h3>
          <p className="text-xl font-bold text-green-500">{data.status.database}</p>
        </div>
      </div>

      <h3 className="text-lg font-semibold mb-4">Traffic & Threat Metrics</h3>
      {data.metrics.total_traffic_analyzed === 0 ? (
        <div className="bg-slate-900 p-12 text-center rounded border border-slate-800">
           <Activity className="mx-auto text-slate-600 mb-4" size={48} />
           <p className="text-slate-400 text-xl font-bold tracking-widest">NO DATA AVAILABLE</p>
           <p className="text-slate-500 mt-2">Upload a PCAP to begin analysis</p>
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-6">
          <div className="bg-slate-900 p-6 rounded border border-slate-800">
            <h4 className="text-sm text-slate-400 mb-2">Flows Analyzed</h4>
            <p className="text-3xl">{data.metrics.flows_analyzed}</p>
          </div>
          <div className="bg-slate-900 p-6 rounded border border-slate-800">
            <h4 className="text-sm text-slate-400 mb-2">Threats Detected</h4>
            <p className="text-3xl text-red-500">{data.metrics.threats_detected}</p>
          </div>
          <div className="bg-slate-900 p-6 rounded border border-slate-800">
            <h4 className="text-sm text-slate-400 mb-2">Anomalies Detected</h4>
            <p className="text-3xl text-yellow-500">{data.metrics.anomalies_detected}</p>
          </div>
        </div>
      )}
    </div>
  );
}
''',
    'frontend/src/pages/Alerts.tsx': '''import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAlerts } from "../services/api";

export default function Alerts() {
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    getAlerts().then(res => setAlerts(res.data)).catch(console.error);
  }, []);

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6">Threat Alerts</h2>
      
      {alerts.length === 0 ? (
        <div className="bg-slate-900 p-12 text-center rounded border border-slate-800 text-slate-400">
           NO ALERTS
        </div>
      ) : (
        <div className="bg-slate-900 rounded border border-slate-800 overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 text-sm">
              <tr>
                <th className="p-4">Time</th>
                <th className="p-4">Source</th>
                <th className="p-4">Destination</th>
                <th className="p-4">Threat Type</th>
                <th className="p-4">Severity</th>
                <th className="p-4">Risk Score</th>
                <th className="p-4">Action</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map(a => (
                <tr key={a.id} className="border-b border-slate-800 hover:bg-slate-800/50">
                  <td className="p-4 text-sm">{new Date(a.timestamp).toLocaleString()}</td>
                  <td className="p-4">{a.source_ip}:{a.source_port}</td>
                  <td className="p-4">{a.destination_ip}:{a.destination_port}</td>
                  <td className="p-4 font-semibold">{a.threat_type}</td>
                  <td className="p-4">
                    <span className={px-2 py-1 text-xs rounded font-bold }>
                      {a.severity}
                    </span>
                  </td>
                  <td className="p-4">{a.risk_score}</td>
                  <td className="p-4">
                    <Link to={/alerts/} className="text-blue-500 hover:underline text-sm">Investigate</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
''',
    'frontend/src/pages/AlertDetail.tsx': '''import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getAlertById } from "../services/api";
import { ArrowLeft, ShieldAlert } from "lucide-react";

export default function AlertDetail() {
  const { id } = useParams();
  const [alert, setAlert] = useState<any>(null);

  useEffect(() => {
    if(id) {
      getAlertById(id).then(res => setAlert(res.data)).catch(console.error);
    }
  }, [id]);

  if (!alert) return <div className="p-8 text-slate-400">Loading alert details...</div>;

  return (
    <div className="p-8">
      <Link to="/alerts" className="text-slate-400 hover:text-white flex items-center gap-2 mb-6 text-sm">
        <ArrowLeft size={16} /> Back to Alerts
      </Link>
      
      <div className="bg-slate-900 border border-slate-800 rounded p-6">
        <div className="flex items-start justify-between border-b border-slate-800 pb-6 mb-6">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-3">
              <ShieldAlert className={alert.severity === 'CRITICAL' ? 'text-red-500' : 'text-orange-500'} /> 
              {alert.threat_type}
            </h2>
            <p className="text-slate-400 mt-2">Detected at {new Date(alert.timestamp).toLocaleString()}</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-slate-400">Risk Score</div>
            <div className="text-3xl font-bold">{alert.risk_score}</div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-4 text-slate-300">Connection Details</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between border-b border-slate-800 pb-2">
                <span className="text-slate-400">Source IP</span>
                <span className="font-mono">{alert.source_ip}</span>
              </div>
              <div className="flex justify-between border-b border-slate-800 pb-2">
                <span className="text-slate-400">Source Port</span>
                <span className="font-mono">{alert.source_port}</span>
              </div>
              <div className="flex justify-between border-b border-slate-800 pb-2">
                <span className="text-slate-400">Destination IP</span>
                <span className="font-mono">{alert.destination_ip}</span>
              </div>
              <div className="flex justify-between border-b border-slate-800 pb-2">
                <span className="text-slate-400">Destination Port</span>
                <span className="font-mono">{alert.destination_port}</span>
              </div>
              <div className="flex justify-between border-b border-slate-800 pb-2">
                <span className="text-slate-400">Protocol</span>
                <span className="font-mono">{alert.protocol}</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-4 text-slate-300">Detection Evidence</h3>
            <p className="text-sm text-slate-400 mb-4">
              WHY WAS THIS DETECTED? The following evidence contributed to the risk score:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-sm">
              {Array.isArray(alert.evidence) ? alert.evidence.map((ev: string, i: int) => (
                <li key={i} className="text-slate-300">{ev}</li>
              )) : (
                <li className="text-slate-300">{JSON.stringify(alert.evidence)}</li>
              )}
            </ul>

            <div className="mt-8 bg-slate-950 p-4 rounded border border-slate-800">
               <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Model Context</div>
               <div className="text-sm">Engine: {alert.model_used}</div>
               <div className="text-sm">Anomaly Score: {alert.anomaly_score}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
''',
    'frontend/src/pages/PcapUpload.tsx': '''import React, { useState } from "react";
import { uploadPcap } from "../services/api";
import { UploadCloud, CheckCircle, XCircle, Loader2 } from "lucide-react";

export default function PcapUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [result, setResult] = useState<any>(null);

  const handleUpload = async () => {
    if (!file) return;
    setStatus("uploading");
    try {
      const res = await uploadPcap(file);
      setResult(res.data);
      setStatus("success");
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  };

  return (
    <div className="p-8 max-w-3xl">
      <h2 className="text-2xl font-bold mb-6">Controlled PCAP Analysis</h2>
      <p className="text-slate-400 mb-8">
        Upload a PCAP file to simulate passive one-way traffic ingestion. 
        The system will extract normalized events, build windowed features, and run hybrid threat detection.
      </p>

      <div className="bg-slate-900 border border-slate-800 rounded p-8 text-center">
        <UploadCloud className="mx-auto text-slate-500 mb-4" size={48} />
        <input 
          type="file" 
          accept=".pcap,.pcapng" 
          onChange={e => setFile(e.target.files?.[0] || null)}
          className="block w-full max-w-sm mx-auto mb-6 text-sm text-slate-400
            file:mr-4 file:py-2 file:px-4
            file:rounded file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-500 file:text-white
            hover:file:bg-blue-600 cursor-pointer"
        />
        
        <button 
          onClick={handleUpload}
          disabled={!file || status === "uploading"}
          className="bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white font-bold py-2 px-6 rounded transition flex items-center justify-center gap-2 mx-auto"
        >
          {status === "uploading" && <Loader2 className="animate-spin" size={18} />}
          Analyze Traffic
        </button>
      </div>

      {status === "success" && result && (
        <div className="mt-8 bg-green-500/10 border border-green-500/30 p-6 rounded flex items-start gap-4">
          <CheckCircle className="text-green-500 shrink-0" />
          <div>
            <h3 className="font-bold text-green-500 mb-2">Analysis Complete</h3>
            <ul className="text-sm space-y-1 text-slate-300">
              <li>Events Ingested: {result.events_ingested}</li>
              <li>Flows Analyzed: {result.flows_analyzed}</li>
              <li>Threats Detected: <span className="font-bold text-white">{result.threats_detected}</span></li>
            </ul>
            <p className="mt-4 text-sm text-slate-400">Check the Alerts dashboard to view detections.</p>
          </div>
        </div>
      )}

      {status === "error" && (
        <div className="mt-8 bg-red-500/10 border border-red-500/30 p-6 rounded flex items-start gap-4">
          <XCircle className="text-red-500 shrink-0" />
          <div>
            <h3 className="font-bold text-red-500">Analysis Failed</h3>
            <p className="text-sm text-slate-400 mt-1">Check console or backend logs for details.</p>
          </div>
        </div>
      )}
    </div>
  );
}
'''
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
