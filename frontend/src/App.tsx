import React from "react";
import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Alerts from "./pages/Alerts";
import AlertDetail from "./pages/AlertDetail";
import PcapUpload from "./pages/PcapUpload";
import Models from "./pages/Models";
import System from "./pages/System";
import Traffic from "./pages/Traffic";
import Monitor from "./pages/Monitor";
import { Activity, ShieldAlert, UploadCloud, BrainCircuit, Server, Radio, BarChart2 } from "lucide-react";
import "./index.css";

function App() {
  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-3 p-3 rounded transition-colors text-sm font-medium ${
      isActive 
        ? "bg-slate-800 text-blue-400 border-l-4 border-blue-500" 
        : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 border-l-4 border-transparent"
    }`;

  return (
    <Router>
      <div className="flex h-screen bg-slate-950 text-slate-100 font-sans selection:bg-blue-500/30">
        <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shadow-2xl z-10">
          <div className="p-6 border-b border-slate-800 bg-slate-900/50">
            <h1 className="text-xl font-bold tracking-wider text-blue-500 flex items-center gap-3">
              <ShieldAlert className="text-blue-500" /> SOC IDS
            </h1>
            <p className="text-[10px] text-slate-500 mt-2 uppercase tracking-widest font-semibold">
              Unidirectional Intel
            </p>
          </div>
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            <div className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2 ml-3 mt-2">Analysis</div>
            <NavLink to="/" className={navLinkClass}>
              <Activity size={18} /> Dashboard
            </NavLink>
            <NavLink to="/monitor" className={navLinkClass}>
              <Radio size={18} /> Live Monitor
            </NavLink>
            <NavLink to="/traffic" className={navLinkClass}>
              <BarChart2 size={18} /> Traffic Analytics
            </NavLink>
            
            <div className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2 ml-3 mt-6">Detection</div>
            <NavLink to="/alerts" className={navLinkClass}>
              <ShieldAlert size={18} /> Alerts
            </NavLink>
            <NavLink to="/models" className={navLinkClass}>
              <BrainCircuit size={18} /> Models
            </NavLink>

            <div className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2 ml-3 mt-6">Ingestion</div>
            <NavLink to="/pcap" className={navLinkClass}>
              <UploadCloud size={18} /> PCAP Analysis
            </NavLink>
            
            <div className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2 ml-3 mt-6">System</div>
            <NavLink to="/system" className={navLinkClass}>
              <Server size={18} /> System Health
            </NavLink>
          </nav>
        </aside>
        <main className="flex-1 overflow-y-auto bg-slate-950">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/monitor" element={<Monitor />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/alerts/:id" element={<AlertDetail />} />
            <Route path="/traffic" element={<Traffic />} />
            <Route path="/pcap" element={<PcapUpload />} />
            <Route path="/models" element={<Models />} />
            <Route path="/system" element={<System />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
