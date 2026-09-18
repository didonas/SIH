import os

files = {
    'frontend/src/pages/Dashboard.tsx': """import React, { useEffect, useState } from "react";
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
            <div className={`text-sm font-bold ${
              ['ONLINE', 'LOADED', 'CONNECTED', 'AVAILABLE', 'ACTIVE'].includes(item.val) 
                ? 'text-green-500' 
                : item.val === 'IDLE' ? 'text-slate-300' : 'text-red-500'
            }`}>
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
""",
    'frontend/src/pages/Alerts.tsx': """import React, { useEffect, useState } from "react";
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
                      <span className={`px-2.5 py-1 text-[10px] uppercase tracking-wider rounded-md font-bold border ${
                        a.severity === 'CRITICAL' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                        a.severity === 'HIGH' ? 'bg-orange-500/10 text-orange-400 border-orange-500/20' :
                        a.severity === 'MEDIUM' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                        'bg-slate-500/10 text-slate-400 border-slate-500/20'
                      }`}>
                        {a.severity}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm font-mono">
                      <span className={a.risk_score >= 80 ? 'text-red-400 font-bold' : 'text-slate-300'}>{a.risk_score}</span>
                    </td>
                    <td className="px-6 py-4">
                      <Link to={`/alerts/${a.id}`} className="text-blue-400 hover:text-blue-300 font-medium text-sm transition-colors">Investigate &rarr;</Link>
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
""",
    'frontend/src/pages/AlertDetail.tsx': """import React, { useEffect, useState } from "react";
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
              <span className={`px-3 py-1 text-xs rounded-md font-bold uppercase tracking-wider border ${
                alert.severity === 'CRITICAL' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                alert.severity === 'HIGH' ? 'bg-orange-500/10 text-orange-400 border-orange-500/20' :
                alert.severity === 'MEDIUM' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                'bg-slate-500/10 text-slate-400 border-slate-500/20'
              }`}>
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
""",
    'frontend/src/pages/System.tsx': """import React, { useEffect, useState } from "react";
import api from "../services/api";
import { Server, Cpu, HardDrive, Activity } from "lucide-react";

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

  if (!sys) return <div className="p-8 text-slate-400 font-mono animate-pulse">Querying system endpoints...</div>;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <header className="mb-8">
        <h2 className="text-3xl font-bold tracking-tight mb-2 flex items-center gap-3">
          <Server className="text-green-500" /> System Health
        </h2>
        <p className="text-slate-400 text-sm">Host metrics and component status.</p>
      </header>
      
      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-xl flex items-start gap-4">
           <Cpu className="text-blue-500 shrink-0 mt-1" size={28} />
           <div>
             <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1">CPU Usage</div>
             <div className="text-3xl font-black font-mono text-slate-200">{sys.cpu_usage_percent}%</div>
           </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-xl flex items-start gap-4">
           <HardDrive className="text-purple-500 shrink-0 mt-1" size={28} />
           <div>
             <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1">Memory Usage</div>
             <div className="text-3xl font-black font-mono text-slate-200">{sys.memory_usage_percent}%</div>
           </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-xl flex items-start gap-4">
           <Activity className="text-green-500 shrink-0 mt-1" size={28} />
           <div>
             <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1">Uptime</div>
             <div className="text-3xl font-black font-mono text-slate-200">{sys.uptime_seconds}s</div>
           </div>
        </div>
      </div>

      <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-xl overflow-hidden">
        <div className="bg-slate-950 p-4 border-b border-slate-800">
          <h3 className="font-semibold text-slate-200">Component Status</h3>
        </div>
        <table className="w-full text-left">
          <tbody className="divide-y divide-slate-800/50">
            {Object.entries(sys.components).map(([k, v]) => (
              <tr key={k} className="hover:bg-slate-800/30 transition-colors">
                <td className="p-5 capitalize font-medium text-slate-300 w-1/2">{k.replace('_', ' ')}</td>
                <td className="p-5">
                  <span className={`px-3 py-1 text-xs rounded-md font-bold uppercase tracking-wider border ${
                    v === 'ONLINE' || v === 'CONNECTED' || v === 'AVAILABLE' 
                      ? 'bg-green-500/10 text-green-500 border-green-500/20' 
                      : 'bg-red-500/10 text-red-500 border-red-500/20'
                  }`}>
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
""",
    'frontend/src/pages/PcapUpload.tsx': """import React, { useState } from "react";
import { uploadPcap } from "../services/api";
import { UploadCloud, File, Activity, CheckCircle, AlertTriangle } from "lucide-react";

export default function PcapUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState("IDLE");
  const [result, setResult] = useState<any>(null);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    
    setStatus("ANALYZING");
    setResult(null);
    try {
      const res = await uploadPcap(file);
      setResult(res.data);
      setStatus("COMPLETED");
    } catch (err) {
      console.error(err);
      setStatus("ERROR");
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <header className="mb-8">
        <h2 className="text-3xl font-bold tracking-tight mb-2">PCAP Analysis</h2>
        <p className="text-slate-400 text-sm">Upload packet captures for offline feature extraction and threat detection.</p>
      </header>

      <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-xl overflow-hidden mb-8">
        <form onSubmit={handleUpload} className="p-8">
          <div className="border-2 border-dashed border-slate-700 rounded-xl p-12 text-center hover:border-blue-500 transition-colors bg-slate-950/50">
            <input 
              type="file" 
              accept=".pcap,.pcapng" 
              onChange={e => setFile(e.target.files?.[0] || null)} 
              className="hidden" 
              id="pcap-upload" 
            />
            <label htmlFor="pcap-upload" className="cursor-pointer flex flex-col items-center">
              <UploadCloud size={48} className="text-blue-500 mb-4" />
              <span className="text-lg font-medium text-slate-200">
                {file ? file.name : "Select a PCAP file"}
              </span>
              <span className="text-sm text-slate-500 mt-2">
                {file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : "Click to browse"}
              </span>
            </label>
          </div>
          
          <div className="mt-6 flex justify-end">
            <button 
              type="submit" 
              disabled={!file || status === "ANALYZING"}
              className="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-500 text-white px-8 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2"
            >
              {status === "ANALYZING" ? (
                <><Activity className="animate-spin" size={18} /> Analyzing...</>
              ) : "Run Analysis"}
            </button>
          </div>
        </form>
      </div>

      {status === "COMPLETED" && result && (
        <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-xl overflow-hidden animate-in fade-in slide-in-from-bottom-4">
          <div className="bg-green-500/10 p-4 border-b border-green-500/20 flex items-center gap-3">
            <CheckCircle className="text-green-500" size={20} />
            <h3 className="font-semibold text-green-400 tracking-wide">Analysis Completed Successfully</h3>
          </div>
          <div className="p-6 grid grid-cols-4 gap-6">
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
              <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1">Packets Parsed</div>
              <div className="text-2xl font-mono text-slate-200">{result.events_ingested}</div>
            </div>
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
              <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1">Flows Generated</div>
              <div className="text-2xl font-mono text-slate-200">{result.flows_analyzed}</div>
            </div>
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
              <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1">Processing Time</div>
              <div className="text-2xl font-mono text-slate-200">{result.processing_time_ms}ms</div>
            </div>
            <div className="bg-slate-950 p-4 rounded-lg border border-red-900/50 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-red-500"></div>
              <div className="text-xs text-red-500/80 font-semibold uppercase tracking-wider mb-1 pl-2">Threats Found</div>
              <div className="text-2xl font-mono text-red-400 pl-2">{result.threats_detected}</div>
            </div>
          </div>
        </div>
      )}

      {status === "ERROR" && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6 flex items-start gap-4 text-red-400">
          <AlertTriangle size={24} className="shrink-0 mt-1" />
          <div>
            <h3 className="font-bold text-lg mb-1">Analysis Failed</h3>
            <p className="text-sm text-red-400/80">The system encountered an error while processing the PCAP. Please verify the file format and integrity.</p>
          </div>
        </div>
      )}
    </div>
  );
}
"""
}

for path, content in files.items():
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
