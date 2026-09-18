import React, { useEffect, useState } from "react";
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
