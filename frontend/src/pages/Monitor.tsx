import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getLiveInterfaces, startLiveCapture, stopLiveCapture, getLiveStatus } from "../services/api";
import { Radio, Play, Square, Activity, AlertTriangle, ShieldAlert } from "lucide-react";

export default function Monitor() {
  const [interfaces, setInterfaces] = useState<{id: string, display: string}[]>([]);
  const [selectedIface, setSelectedIface] = useState("");
  const [status, setStatus] = useState<any>({ 
    status: "STOPPED", 
    packets_observed: 0, 
    flows_observed: 0, 
    alerts_generated: 0,
    recent_alerts: []
  });

  useEffect(() => {
    getLiveInterfaces().then(res => {
      const ifaces = res.data.interfaces || [];
      setInterfaces(ifaces);
      if (ifaces.length > 0) {
         setSelectedIface(ifaces[0].id);
      }
    }).catch(err => {
      console.error(err);
      setErrorMsg("Failed to load network interfaces. Npcap driver may be locked or unavailable.");
    });
  }, []);

  useEffect(() => {
    const intv = setInterval(() => {
      getLiveStatus().then(res => setStatus(res.data)).catch(console.error);
    }, 2000);
    return () => clearInterval(intv);
  }, []);

  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleStart = async () => {
    setErrorMsg(null);
    try {
      await startLiveCapture(selectedIface);
      // Immediately reset UI counters to match new session expectation
      setStatus({ status: "ACTIVE", packets_observed: 0, flows_observed: 0, alerts_generated: 0, recent_alerts: [] });
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || err.message || "Failed to start capture");
      setStatus({ ...status, status: "ERROR" });
    }
  };

  const handleStop = async () => {
    try {
      await stopLiveCapture();
      setStatus({ ...status, status: "STOPPED" });
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto h-full flex flex-col overflow-hidden">
      <header className="mb-6 flex flex-col md:flex-row md:justify-between md:items-end gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight mb-2 flex items-center gap-3">
            <Radio className={status.status === "ACTIVE" ? "text-blue-500 animate-pulse" : "text-slate-500"} /> Live Monitor
          </h2>
          <p className="text-slate-400 text-sm font-semibold tracking-wide uppercase flex items-center gap-2">
            Passive Analysis Stream
            {status.status === "ACTIVE" ? (
              <span className="bg-green-500/10 text-green-500 px-2 py-0.5 rounded text-xs border border-green-500/20">CAPTURE ACTIVE</span>
            ) : status.status === "ERROR" ? (
              <span className="bg-red-500/10 text-red-500 px-2 py-0.5 rounded text-xs border border-red-500/20">CAPTURE ERROR</span>
            ) : (
              <span className="bg-slate-800 text-slate-400 px-2 py-0.5 rounded text-xs">CAPTURE STOPPED</span>
            )}
          </p>
        </div>
        
        <div className="flex gap-4 items-center bg-slate-900 p-3 rounded-lg border border-slate-800 w-full md:w-auto overflow-hidden">
          <select 
            value={selectedIface} 
            onChange={e => setSelectedIface(e.target.value)}
            disabled={status.status === "ACTIVE"}
            className="bg-slate-950 border border-slate-700 rounded px-3 py-1.5 text-sm text-slate-200 outline-none focus:border-blue-500 disabled:opacity-50 flex-1 min-w-0 text-ellipsis overflow-hidden"
          >
            {interfaces.map(iface => <option key={iface.id} value={iface.id}>{iface.display}</option>)}
          </select>
          {status.status === "ACTIVE" ? (
            <button onClick={handleStop} className="bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/20 px-4 py-1.5 rounded flex items-center gap-2 text-sm font-bold transition-colors shrink-0">
              <Square size={14} fill="currentColor" /> Stop
            </button>
          ) : (
            <button onClick={handleStart} disabled={!selectedIface} className="bg-green-500/10 hover:bg-green-500/20 text-green-500 border border-green-500/20 px-4 py-1.5 rounded flex items-center gap-2 text-sm font-bold transition-colors disabled:opacity-50 shrink-0">
              <Play size={14} fill="currentColor" /> Start Capture
            </button>
          )}
        </div>
      </header>

      {status.error && (
        <div className="bg-red-500/10 border border-red-500/20 p-4 rounded-lg mb-6 flex items-start gap-3 text-red-400 text-sm">
          <AlertTriangle size={18} className="shrink-0 mt-0.5" />
          <div>{status.error}</div>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-md relative">
           <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider mb-2">Packets Observed</div>
           <div className="text-3xl font-mono text-slate-200">{status.packets_observed.toLocaleString()}</div>
           {status.status === "STOPPED" && status.packets_observed > 0 && <span className="absolute top-6 right-6 text-[9px] font-bold text-slate-600 bg-slate-800 px-2 py-1 rounded">SESSION TOTAL</span>}
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-md relative">
           <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider mb-2">Flows Aggregated</div>
           <div className="text-3xl font-mono text-slate-200">{status.flows_observed.toLocaleString()}</div>
           {status.status === "STOPPED" && status.flows_observed > 0 && <span className="absolute top-6 right-6 text-[9px] font-bold text-slate-600 bg-slate-800 px-2 py-1 rounded">SESSION TOTAL</span>}
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-md relative">
           <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider mb-2">Live Detections</div>
           <div className="flex justify-between items-center">
             <div className="text-3xl font-mono text-red-500">{status.alerts_generated.toLocaleString()}</div>
             <div className="text-right">
               <div className="text-sm font-bold text-slate-300 mb-1">Risk Assessed</div>
               <div className={`text-2xl font-black ${status.alerts_generated > 0 ? 'text-red-500 animate-pulse' : 'text-slate-400'}`}>
                  {status.alerts_generated > 0 ? 'THREAT' : 'NORMAL'}
               </div>
             </div>
           </div>
           {status.status === "STOPPED" && status.alerts_generated > 0 && <span className="absolute top-2 right-6 text-[9px] font-bold text-slate-600 bg-slate-800 px-2 py-1 rounded">SESSION TOTAL</span>}
        </div>
      </div>

      {errorMsg && (
        <div className="mt-6 bg-red-500/10 border border-red-500/20 rounded-lg p-4 flex items-center gap-4 text-red-400">
           <AlertTriangle size={24} className="shrink-0" />
           <div>
              <p className="font-bold">Live Capture Error</p>
              <p className="text-sm font-mono mt-1">{errorMsg}</p>
           </div>
        </div>
      )}

      <div className="flex-1 bg-slate-900 rounded-xl border border-slate-800 shadow-xl overflow-hidden flex flex-col min-h-0">
        <div className="bg-slate-950 p-4 border-b border-slate-800 flex items-center justify-between shrink-0">
          <h3 className="font-semibold text-slate-200 tracking-wide uppercase flex items-center gap-2">
            <Activity size={18} className="text-blue-500" /> Recent Live Alerts (Current Session)
          </h3>
          <span className="text-xs text-slate-500 font-mono">Updates automatically</span>
        </div>
        <div className="p-0 overflow-y-auto flex-1">
          {status.recent_alerts && status.recent_alerts.length > 0 ? (
            <table className="w-full text-left">
              <thead className="bg-slate-900 sticky top-0 text-[10px] text-slate-500 uppercase tracking-wider border-b border-slate-800 z-10">
                <tr>
                  <th className="py-3 px-6">Timestamp</th>
                  <th className="py-3 px-6">Source &rarr; Destination</th>
                  <th className="py-3 px-6">Type</th>
                  <th className="py-3 px-6">Severity</th>
                  <th className="py-3 px-6">Risk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {status.recent_alerts.map((a: any) => (
                  <tr key={a.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-4 px-6 text-sm font-mono text-slate-400">
                      {a.timestamp ? new Date(a.timestamp).toLocaleTimeString() : 'N/A'}
                    </td>
                    <td className="py-4 px-6 text-sm font-mono text-slate-300">
                      {a.source_ip}:{a.source_port} <span className="text-slate-600 mx-1">&rarr;</span> {a.destination_ip}:{a.destination_port}
                      <span className="ml-2 text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-slate-400">{a.protocol}</span>
                    </td>
                    <td className="py-4 px-6 text-sm font-bold text-red-400">{a.threat_type}</td>
                    <td className="py-4 px-6">
                      <span className={`px-2 py-1 text-[10px] rounded font-bold uppercase tracking-wider border ${
                        a.severity === 'CRITICAL' ? 'bg-red-500/10 text-red-500 border-red-500/20' :
                        a.severity === 'HIGH' ? 'bg-orange-500/10 text-orange-500 border-orange-500/20' :
                        'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'
                      }`}>{a.severity}</span>
                    </td>
                    <td className="py-4 px-6 text-sm font-mono font-bold text-slate-200">
                      {a.risk_score}
                      <Link to={`/alerts/${a.id}`} className="ml-4 text-xs font-sans text-blue-500 hover:underline">Investigate</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
             <div className="h-full flex flex-col items-center justify-center text-slate-500 p-12">
               <ShieldAlert size={48} className="mb-4 text-slate-700" />
               <p className="font-semibold text-lg">No live threats detected in current session.</p>
               <p className="text-sm mt-1">Make sure capture is active and generating traffic.</p>
             </div>
          )}
        </div>
      </div>
    </div>
  );
}
