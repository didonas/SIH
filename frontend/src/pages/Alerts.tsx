import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAlerts } from "../services/api";
import { ShieldAlert, Search } from "lucide-react";

export default function Alerts() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAlerts()
      .then(res => setAlerts(res.data))
      .catch(err => setError("Failed to fetch alerts."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 text-slate-400 font-mono animate-pulse">Loading threat intelligence...</div>;
  if (error) return <div className="p-8 text-red-400 font-mono">Error: {error}</div>;

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
