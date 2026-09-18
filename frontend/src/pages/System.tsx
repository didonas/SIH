import React, { useEffect, useState } from "react";
import api from "../services/api";
import { Server, Cpu, HardDrive, Activity } from "lucide-react";

export default function System() {
  const [sys, setSys] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSys = () => {
      api.get("/system")
         .then(res => { setSys(res.data); setError(null); })
         .catch(err => setError("System health endpoints unreachable."));
    };
    fetchSys();
    const intv = setInterval(fetchSys, 5000);
    return () => clearInterval(intv);
  }, []);

  if (error && !sys) return <div className="p-8 text-red-400 font-mono">Error: {error}</div>;
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
