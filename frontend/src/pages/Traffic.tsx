import React, { useEffect, useState } from "react";
import { getTrafficAnalytics } from "../services/api";
import { BarChart2, Activity, Network, ShieldAlert, Target } from "lucide-react";

export default function Traffic() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTrafficAnalytics()
      .then(res => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 text-slate-400 font-mono animate-pulse">Aggregating intelligence data...</div>;

  if (!data || data.metrics.total_events === 0) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <header className="mb-8">
          <h2 className="text-3xl font-bold tracking-tight mb-2 flex items-center gap-3">
            <BarChart2 className="text-blue-500" /> Traffic Analytics
          </h2>
          <p className="text-slate-400 text-sm">Visual analysis of network patterns and flow distributions.</p>
        </header>
        <div className="bg-slate-900 border border-slate-800 p-16 rounded-xl text-center text-slate-500 shadow-xl">
          <BarChart2 size={48} className="mx-auto mb-4 text-slate-700" />
          <p className="text-xl font-medium text-slate-300">NO DATA AVAILABLE</p>
          <p className="text-sm mt-2">Historical traffic aggregates have not been compiled for this view. Process a PCAP to populate.</p>
        </div>
      </div>
    );
  }

  const { metrics, distributions } = data;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <header>
        <h2 className="text-3xl font-bold tracking-tight mb-2 flex items-center gap-3">
          <BarChart2 className="text-blue-500" /> Traffic Analytics
        </h2>
        <p className="text-slate-400 text-sm">Aggregated flow statistics and threat distributions.</p>
      </header>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-5 gap-6">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-md">
           <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider mb-2 flex items-center gap-2"><Network size={14}/> Total Events / Packets</div>
           <div className="text-3xl font-mono text-slate-200">{metrics.total_events.toLocaleString()}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-md">
           <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider mb-2 flex items-center gap-2"><Activity size={14}/> Total Flows Analyzed</div>
           <div className="text-3xl font-mono text-slate-200">{metrics.total_flows.toLocaleString()}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-md">
           <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider mb-2 flex items-center gap-2"><ShieldAlert size={14}/> Total Alerts Triggered</div>
           <div className="text-3xl font-mono text-red-500">{metrics.total_alerts.toLocaleString()}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-md">
           <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider mb-2">Anomalies Isolated</div>
           <div className="text-3xl font-mono text-orange-500">{metrics.anomalies_detected.toLocaleString()}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-md">
           <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider mb-2">Throughput Speed</div>
           <div className="text-3xl font-mono text-slate-200">{metrics.flows_per_second}<span className="text-sm font-sans text-slate-500 ml-1">flows/sec</span></div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-8">
         {/* Protocol & Threat Distribution */}
         <div className="space-y-8">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md">
               <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-6">Threat Protocol Distribution</h3>
               <div className="space-y-4">
                  {Object.entries(distributions.protocols).length > 0 ? Object.entries(distributions.protocols).map(([protocol, count]: [string, any]) => {
                     const pct = Math.min((count / metrics.total_alerts) * 100, 100);
                     return (
                        <div key={protocol}>
                           <div className="flex justify-between text-xs font-mono mb-1 text-slate-400">
                              <span>{protocol}</span>
                              <span>{count} alerts</span>
                           </div>
                           <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden">
                              <div className="bg-blue-500 h-full rounded-full" style={{ width: `${pct}%` }}></div>
                           </div>
                        </div>
                     )
                  }) : <div className="text-sm text-slate-500 italic">No protocols associated with alerts.</div>}
               </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md">
               <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-6">Threat Type Breakdown</h3>
               <div className="space-y-4">
                  {Object.entries(distributions.threat_types).length > 0 ? Object.entries(distributions.threat_types).map(([threat, count]: [string, any]) => {
                     const pct = Math.min((count / metrics.total_alerts) * 100, 100);
                     return (
                        <div key={threat}>
                           <div className="flex justify-between text-xs font-mono mb-1 text-slate-400">
                              <span className="font-bold text-slate-300">{threat}</span>
                              <span>{count}</span>
                           </div>
                           <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden">
                              <div className="bg-red-500 h-full rounded-full" style={{ width: `${pct}%` }}></div>
                           </div>
                        </div>
                     )
                  }) : <div className="text-sm text-slate-500 italic">No threats categorized.</div>}
               </div>
            </div>
         </div>

         {/* Sources & Destinations */}
         <div className="space-y-8">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md">
               <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-6 flex items-center gap-2">
                  <Target size={16} className="text-orange-500"/> Top Threat Sources
               </h3>
               <table className="w-full text-left">
                  <thead className="bg-slate-950/50 text-[10px] text-slate-500 uppercase tracking-wider">
                     <tr>
                        <th className="py-2 px-4 rounded-l-lg">IP Address</th>
                        <th className="py-2 px-4 rounded-r-lg text-right">Alerts Triggered</th>
                     </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                     {distributions.top_sources.length > 0 ? distributions.top_sources.map((s: any, idx: number) => (
                        <tr key={idx}>
                           <td className="py-3 px-4 font-mono text-sm text-slate-300">{s.ip}</td>
                           <td className="py-3 px-4 font-mono text-sm text-red-400 text-right font-bold">{s.count}</td>
                        </tr>
                     )) : <tr><td colSpan={2} className="py-4 text-center text-sm text-slate-500 italic">No sources recorded</td></tr>}
                  </tbody>
               </table>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md">
               <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-6 flex items-center gap-2">
                  <Target size={16} className="text-green-500"/> Top Targeted Destinations
               </h3>
               <table className="w-full text-left">
                  <thead className="bg-slate-950/50 text-[10px] text-slate-500 uppercase tracking-wider">
                     <tr>
                        <th className="py-2 px-4 rounded-l-lg">IP Address</th>
                        <th className="py-2 px-4 rounded-r-lg text-right">Hits</th>
                     </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                     {distributions.top_destinations.length > 0 ? distributions.top_destinations.map((s: any, idx: number) => (
                        <tr key={idx}>
                           <td className="py-3 px-4 font-mono text-sm text-slate-300">{s.ip}</td>
                           <td className="py-3 px-4 font-mono text-sm text-orange-400 text-right font-bold">{s.count}</td>
                        </tr>
                     )) : <tr><td colSpan={2} className="py-4 text-center text-sm text-slate-500 italic">No destinations recorded</td></tr>}
                  </tbody>
               </table>
            </div>
         </div>
      </div>
    </div>
  );
}
