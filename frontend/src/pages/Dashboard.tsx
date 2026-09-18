import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import { Activity, ShieldAlert, Cpu, Database, Network } from "lucide-react";

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get("/dashboard/summary")
       .then(res => setData(res.data))
       .catch(err => setError(err.response?.data?.detail || err.message || "Failed to load dashboard"));
  }, []);

  if (error) return <div className="p-8 text-red-400 font-mono">Error: {error}</div>;
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
