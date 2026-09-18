import os

files = {
    'backend/app/routers/analyze.py': """from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database import models
import shutil
import os
import time
import pandas as pd
from app.ingestion.pcap_adapter import parse_pcap_to_events
from app.feature_engineering.window_engine import create_flow_features
from app.detection.rules import evaluate_rules
from app.detection.risk_scoring import calculate_risk
from app.ml.engine import MLEngine

router = APIRouter(prefix="/api/analyze", tags=["analyze"])
ml_engine = MLEngine()

global_traffic_status = "IDLE"

@router.post("/pcap")
async def analyze_pcap(file: UploadFile = File(...), db: Session = Depends(get_db)):
    global global_traffic_status
    if not file.filename.endswith('.pcap') and not file.filename.endswith('.pcapng'):
        raise HTTPException(status_code=400, detail="Invalid file format")
        
    global_traffic_status = "ANALYZING"
    start_time = time.time()
    os.makedirs("tmp", exist_ok=True)
    safe_filename = os.path.basename(file.filename)
    file_path = f"tmp/{safe_filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        events = parse_pcap_to_events(file_path)
        if not events:
            global_traffic_status = "IDLE"
            return {"message": "No events found", "alerts": []}
            
        df = create_flow_features(events)
        if df.empty:
            global_traffic_status = "IDLE"
            return {"message": "No flows detected", "alerts": []}
            
        df_rules = evaluate_rules(df)
        df = pd.concat([df, df_rules], axis=1)
        
        df_ml = ml_engine.analyze_flows(df)
        df = pd.concat([df, df_ml], axis=1)
        
        df_risk = df.apply(calculate_risk, axis=1)
        df = pd.concat([df, df_risk], axis=1)
        
        alerts_created = []
        for i, row in df.iterrows():
            if row['final_risk_score'] >= 30:
                alert = models.Alert(
                    source_ip=row['source_ip'],
                    destination_ip=row['destination_ip'],
                    source_port=int(row['source_port']),
                    destination_port=int(row['destination_port']),
                    protocol=str(row['protocol']),
                    threat_type=row['final_threat_type'],
                    severity=row['severity'],
                    risk_score=row['final_risk_score'],
                    confidence=row.get('rf_probability', 0.0),
                    model_used="Rules+ML",
                    anomaly_score=row.get('if_score', 0.0),
                    evidence=row['evidence']
                )
                db.add(alert)
                alerts_created.append(alert)
                
        db.commit()
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        history = models.DetectionHistory(
            input_source=safe_filename,
            model="Rules+ML",
            result=f"{len(alerts_created)} threats detected",
            processing_status="SUCCESS",
            events_ingested=len(events),
            flows_analyzed=len(df),
            alerts_generated=len(alerts_created),
            processing_time_ms=processing_time_ms
        )
        db.add(history)
        db.commit()
        
        alert_list = []
        for a in alerts_created:
            alert_list.append({
                "id": a.id,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                "source_ip": a.source_ip,
                "destination_ip": a.destination_ip,
                "source_port": a.source_port,
                "destination_port": a.destination_port,
                "protocol": a.protocol,
                "threat_type": a.threat_type,
                "severity": a.severity,
                "risk_score": a.risk_score,
                "confidence": a.confidence,
                "model_used": a.model_used,
                "anomaly_score": a.anomaly_score,
                "evidence": a.evidence
            })

        global_traffic_status = "COMPLETED"
        return {
            "message": "Analysis complete",
            "events_ingested": len(events),
            "flows_analyzed": len(df),
            "threats_detected": len(alerts_created),
            "processing_time_ms": processing_time_ms,
            "alerts": alert_list
        }
    except Exception as e:
        global_traffic_status = "ERROR"
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@router.get("/status")
def get_traffic_status():
    global global_traffic_status
    return {"status": global_traffic_status}
""",
    'frontend/src/pages/PcapUpload.tsx': """import React, { useState } from "react";
import { uploadPcap } from "../services/api";
import { Link } from "react-router-dom";
import { UploadCloud, Activity, CheckCircle, AlertTriangle, ShieldAlert, Target, FileText } from "lucide-react";

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
    <div className="p-8 max-w-6xl mx-auto">
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
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4">
          {/* Summary Section */}
          <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-xl overflow-hidden">
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

          {/* Detected Threats Section */}
          {result.alerts && result.alerts.length > 0 ? (
            <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-xl overflow-hidden">
              <div className="bg-slate-950 p-4 border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <ShieldAlert className="text-red-500" size={20} />
                  <h3 className="font-semibold text-slate-200 tracking-wide uppercase">Detected Threats</h3>
                </div>
                <span className="text-sm font-bold text-slate-400">{result.alerts.length} threats detected</span>
              </div>
              <div className="p-6 space-y-6 max-h-[800px] overflow-y-auto">
                {result.alerts.map((alert: any) => (
                  <div key={alert.id} className="bg-slate-950 border border-slate-800 rounded-xl p-6 shadow-inner">
                    <div className="flex justify-between items-start mb-6">
                      <div className="flex items-center gap-4">
                        <span className={`px-3 py-1 text-xs rounded-md font-bold uppercase tracking-wider border ${
                          alert.severity === 'CRITICAL' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                          alert.severity === 'HIGH' ? 'bg-orange-500/10 text-orange-400 border-orange-500/20' :
                          alert.severity === 'MEDIUM' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                          'bg-slate-500/10 text-slate-400 border-slate-500/20'
                        }`}>
                          {alert.severity}
                        </span>
                        <h4 className="text-xl font-bold text-red-400">{alert.threat_type}</h4>
                      </div>
                      <Link to={`/alerts/${alert.id}`} className="bg-blue-600/10 text-blue-500 border border-blue-500/20 hover:bg-blue-600/20 px-4 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center gap-2">
                         Investigate &rarr;
                      </Link>
                    </div>

                    <div className="grid grid-cols-4 gap-6 mb-6">
                      <div>
                        <div className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1 flex items-center gap-1"><Target size={12}/> Source</div>
                        <div className="font-mono text-sm text-slate-300">{alert.source_ip}:{alert.source_port}</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1 flex items-center gap-1"><Target size={12}/> Destination</div>
                        <div className="font-mono text-sm text-slate-300">{alert.destination_ip}:{alert.destination_port}</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1">Protocol</div>
                        <div className="font-mono text-sm text-slate-300">{alert.protocol}</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1">Risk Score</div>
                        <div className="font-mono text-sm text-slate-300 font-bold">{alert.risk_score}/100</div>
                      </div>
                    </div>
                    
                    <div className="bg-slate-900 p-4 rounded-lg border border-slate-800">
                       <h5 className="text-[10px] text-slate-400 font-bold uppercase tracking-widest flex items-center gap-2 mb-3">
                         <FileText size={14} /> Why was this detected?
                       </h5>
                       <ul className="space-y-2">
                         {alert.evidence && alert.evidence.length > 0 ? alert.evidence.map((ev: string, idx: number) => (
                           <li key={idx} className="text-sm font-mono text-slate-300 flex items-start gap-2">
                             <span className="text-blue-500">-</span> {ev}
                           </li>
                         )) : (
                           <li className="text-sm text-slate-500 italic">No specific evidence recorded.</li>
                         )}
                       </ul>
                       <div className="mt-4 pt-4 border-t border-slate-800/50 flex gap-6">
                         <div className="text-xs font-mono text-slate-500"><span className="uppercase font-semibold tracking-wider mr-2 text-slate-600">Model:</span>{alert.model_used}</div>
                         <div className="text-xs font-mono text-slate-500"><span className="uppercase font-semibold tracking-wider mr-2 text-slate-600">Confidence:</span>{(alert.confidence * 100).toFixed(1)}%</div>
                         <div className="text-xs font-mono text-slate-500"><span className="uppercase font-semibold tracking-wider mr-2 text-slate-600">Anomaly Score:</span>{alert.anomaly_score}</div>
                       </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-xl overflow-hidden p-16 flex flex-col items-center justify-center text-slate-400">
               <ShieldAlert size={48} className="mb-4 text-slate-600" />
               <p className="font-semibold text-xl tracking-tight text-slate-300">NO THREATS DETECTED</p>
               <p className="text-sm mt-2 text-slate-500">The analyzed traffic patterns were entirely benign.</p>
            </div>
          )}
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
