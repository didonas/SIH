import os

files = {
    'backend/app/main.py': """from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import engine, Base, get_db
from app.database import models
from app.routers import alerts, analyze, models as models_router, system
from app.config import settings
import shutil
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SIH PS 013 - Threat Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alerts.router)
app.include_router(analyze.router)
app.include_router(models_router.router)
app.include_router(system.router)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0"}

@app.get("/api/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_alerts = db.query(models.Alert).count()
    critical = db.query(models.Alert).filter(models.Alert.severity == 'CRITICAL').count()
    high = db.query(models.Alert).filter(models.Alert.severity == 'HIGH').count()
    medium = db.query(models.Alert).filter(models.Alert.severity == 'MEDIUM').count()
    low = db.query(models.Alert).filter(models.Alert.severity == 'LOW').count()
    
    flows_analyzed = db.query(func.sum(models.DetectionHistory.flows_analyzed)).scalar() or 0
    events_ingested = db.query(func.sum(models.DetectionHistory.events_ingested)).scalar() or 0
    anomalies = db.query(models.Alert).filter(models.Alert.threat_type == 'ANOMALY').count()

    zeek_status = "AVAILABLE" if shutil.which("zeek") else "UNAVAILABLE"
    rf_exists = os.path.exists('models/random_forest.pkl') or os.path.exists('../models/random_forest.pkl')
    ml_status = "LOADED" if rf_exists else "NOT LOADED"

    return {
        "status": {
            "detection_engine": "ONLINE",
            "zeek": zeek_status,
            "ml_model": ml_status,
            "database": "CONNECTED",
            "traffic_input": analyze.global_traffic_status
        },
        "metrics": {
            "total_traffic_analyzed": events_ingested,
            "flows_analyzed": flows_analyzed,
            "threats_detected": total_alerts,
            "critical_alerts": critical,
            "high_alerts": high,
            "medium_alerts": medium,
            "low_alerts": low,
            "anomalies_detected": anomalies
        }
    }

@app.get("/api/dashboard/analytics")
def get_traffic_analytics(db: Session = Depends(get_db)):
    flows_analyzed = db.query(func.sum(models.DetectionHistory.flows_analyzed)).scalar() or 0
    events_ingested = db.query(func.sum(models.DetectionHistory.events_ingested)).scalar() or 0
    processing_time = db.query(func.sum(models.DetectionHistory.processing_time_ms)).scalar() or 0
    
    total_alerts = db.query(models.Alert).count()
    anomalies = db.query(models.Alert).filter(models.Alert.threat_type == 'ANOMALY').count()
    
    protocol_counts = dict(db.query(models.Alert.protocol, func.count(models.Alert.id)).group_by(models.Alert.protocol).all())
    threat_counts = dict(db.query(models.Alert.threat_type, func.count(models.Alert.id)).group_by(models.Alert.threat_type).all())
    severity_counts = dict(db.query(models.Alert.severity, func.count(models.Alert.id)).group_by(models.Alert.severity).all())
    
    top_sources = [{"ip": ip, "count": count} for ip, count in db.query(models.Alert.source_ip, func.count(models.Alert.id)).group_by(models.Alert.source_ip).order_by(func.count(models.Alert.id).desc()).limit(5).all()]
    top_destinations = [{"ip": ip, "count": count} for ip, count in db.query(models.Alert.destination_ip, func.count(models.Alert.id)).group_by(models.Alert.destination_ip).order_by(func.count(models.Alert.id).desc()).limit(5).all()]
    
    history = db.query(models.DetectionHistory).order_by(models.DetectionHistory.detection_time.asc()).all()
    timeline = [{
        "time": h.detection_time.isoformat(), 
        "events": h.events_ingested, 
        "flows": h.flows_analyzed, 
        "alerts": h.alerts_generated
    } for h in history]

    return {
        "metrics": {
            "total_events": events_ingested,
            "total_flows": flows_analyzed,
            "total_alerts": total_alerts,
            "anomalies_detected": anomalies,
            "processing_time_ms": processing_time,
            "flows_per_second": round((flows_analyzed / (processing_time / 1000))) if processing_time > 0 else 0
        },
        "distributions": {
            "protocols": protocol_counts,
            "threat_types": threat_counts,
            "severities": severity_counts,
            "top_sources": top_sources,
            "top_destinations": top_destinations
        },
        "timeline": timeline
    }
""",
    'frontend/src/services/api.ts': """import axios from "axios";

const API_URL = "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_URL,
});

export const getAlerts = () => api.get("/alerts");
export const getAlertById = (id: string) => api.get(`/alerts/${id}`);
export const getModels = () => api.get("/models");
export const getSystemStatus = () => api.get("/system");
export const getTrafficAnalytics = () => api.get("/dashboard/analytics");

export const uploadPcap = (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post("/analyze/pcap", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export default api;
""",
    'frontend/src/pages/Traffic.tsx': """import React, { useEffect, useState } from "react";
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
"""
}

for path, content in files.items():
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
