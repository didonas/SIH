import os

files = {
    'frontend/src/pages/PcapUpload.tsx': '''import React, { useState } from "react";
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
                {file ? ${(file.size / 1024 / 1024).toFixed(2)} MB : "Click to browse"}
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
''',
    'frontend/src/pages/Models.tsx': '''import React, { useEffect, useState } from "react";
import api from "../services/api";
import { BrainCircuit, CheckCircle, XCircle, AlertTriangle, Cpu } from "lucide-react";

export default function Models() {
  const [models, setModels] = useState<any[]>([]);

  useEffect(() => {
    api.get("/models").then(res => setModels(res.data)).catch(console.error);
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <header className="mb-8">
        <h2 className="text-3xl font-bold tracking-tight mb-2 flex items-center gap-3">
          <BrainCircuit className="text-blue-500" /> Detection Models
        </h2>
        <p className="text-slate-400 text-sm">Active machine learning classifiers and anomaly detection engines.</p>
      </header>
      
      <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-6 mb-8 flex gap-4 text-yellow-500/90 shadow-lg">
        <AlertTriangle className="shrink-0 mt-1" size={24} />
        <div>
          <h4 className="font-bold text-lg mb-2 text-yellow-500">Evaluation Methodology Notice</h4>
          <p className="text-sm leading-relaxed text-yellow-500/80">
            The evaluation metrics below are strictly generated by evaluating the models against the unseen 30% fold of the <strong>synthetic demonstration dataset</strong>. Because the dataset relies on highly separable synthetic features (e.g., extremely high packet counts for volumetric flooding vs low counts for normal), the models naturally achieve extremely high theoretical accuracy (e.g., 1.0). These metrics prove the pipeline mathematical integrity, but do <strong>not</strong> represent real-world enterprise detection accuracy.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-8">
        {models.map(m => (
          <div key={m.name} className="bg-slate-900 border border-slate-800 rounded-xl shadow-xl overflow-hidden flex flex-col">
            <div className="p-6 border-b border-slate-800 bg-slate-900/50">
              <div className="flex justify-between items-start mb-1">
                <h3 className="text-xl font-bold text-slate-100">{m.name}</h3>
                {m.status === "LOADED" ? 
                  <span className="flex items-center gap-1.5 text-xs font-bold text-green-500 bg-green-500/10 px-2.5 py-1 rounded-md border border-green-500/20">
                    <CheckCircle size={14} /> LOADED
                  </span> : 
                  <span className="flex items-center gap-1.5 text-xs font-bold text-red-500 bg-red-500/10 px-2.5 py-1 rounded-md border border-red-500/20">
                    <XCircle size={14} /> OFFLINE
                  </span>
                }
              </div>
              <p className="text-sm text-blue-400 font-medium">{m.algorithm}</p>
            </div>
            
            <div className="p-6 flex-1 flex flex-col">
              <div className="grid grid-cols-2 gap-4 mb-8">
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                  <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1">Version</div>
                  <div className="font-mono text-slate-200">{m.version}</div>
                </div>
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                  <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1">Features</div>
                  <div className="font-mono text-slate-200">{m.features} Vector</div>
                </div>
              </div>

              {m.metrics && (
                <div className="mt-auto">
                  <h4 className="text-xs font-bold text-slate-600 mb-4 uppercase tracking-wider flex items-center gap-2">
                    <Cpu size={14} /> Evaluation Metrics (Test Set)
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(m.metrics).map(([k, v]) => (
                      <div key={k} className="flex justify-between items-end border-b border-slate-800/50 pb-2">
                        <span className="text-sm text-slate-400 capitalize">{k.replace('_', ' ')}</span>
                        <span className="text-lg font-mono font-bold text-slate-200">{String(v)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
''',
    'frontend/src/pages/System.tsx': '''import React, { useEffect, useState } from "react";
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
                  <span className={px-3 py-1 text-xs rounded-md font-bold uppercase tracking-wider border }>
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
    'frontend/src/pages/Monitor.tsx': '''import React, { useEffect, useState } from "react";
import api from "../services/api";
import { Radio } from "lucide-react";

export default function Monitor() {
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    const fetchHistory = () => {
      api.get("/dashboard/summary").then(res => {
         // Fallback/dummy polling logic representing stream since backend has no websocket
      });
    };
    fetchHistory();
    const intv = setInterval(fetchHistory, 3000);
    return () => clearInterval(intv);
  }, []);

  return (
    <div className="p-8 max-w-5xl mx-auto h-full flex flex-col">
      <header className="mb-6">
        <h2 className="text-3xl font-bold tracking-tight mb-2 flex items-center gap-3">
          <Radio className="text-blue-500 animate-pulse" /> Live Monitor
        </h2>
        <p className="text-slate-400 text-sm font-semibold tracking-wide uppercase">Passive Analysis Stream</p>
      </header>
      
      <div className="flex-1 bg-black rounded-xl border border-slate-800 shadow-2xl p-6 font-mono text-sm overflow-y-auto">
        <div className="text-slate-500 mb-4 border-b border-slate-800 pb-2 flex justify-between">
          <span>[SYSTEM] Awaiting live ingestion events...</span>
          <span>Only analyzing passive inputs.</span>
        </div>
        {/* Placeholder for real stream logs */}
        <div className="text-slate-600 italic">No live events captured in this session. Process PCAPs to view historical alerts.</div>
      </div>
    </div>
  );
}
''',
    'frontend/src/pages/Traffic.tsx': '''import React from "react";
import { BarChart2 } from "lucide-react";

export default function Traffic() {
  return (
    <div className="p-8 max-w-7xl mx-auto">
      <header className="mb-8">
        <h2 className="text-3xl font-bold tracking-tight mb-2 flex items-center gap-3">
          <BarChart2 className="text-blue-500" /> Traffic Analytics
        </h2>
        <p className="text-slate-400 text-sm">Visual analysis of network patterns.</p>
      </header>
      <div className="bg-slate-900 border border-slate-800 p-16 rounded-xl text-center text-slate-500 shadow-xl">
        <BarChart2 size={48} className="mx-auto mb-4 text-slate-700" />
        <p className="text-lg font-medium">NO DATA AVAILABLE</p>
        <p className="text-sm mt-2">Historical traffic aggregates have not been compiled for this view.</p>
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
