import threading
import time
from app.ingestion.pcap_adapter import parse_packets_to_events
from app.feature_engineering.window_engine import create_flow_features
from app.detection.rules import evaluate_rules
from app.detection.risk_scoring import calculate_risk
from app.ml.engine import MLEngine
from app.database.database import SessionLocal
from app.database import models
import pandas as pd

class LiveCapture:
    def __init__(self):
        self.is_running = False
        self.interface = None
        self.thread = None
        self.buffer = []
        self.lock = threading.Lock()
        self.ml_engine = MLEngine()
        
        self.stats = {
            "packets_observed": 0,
            "flows_observed": 0,
            "alerts_generated": 0,
            "recent_alerts": [],
            "status": "STOPPED",
            "error": None
        }

    def get_interfaces(self):
        try:
            import psutil
            import socket
            results = []
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for name, addr_list in addrs.items():
                if name.startswith("Local Area Connection") or "Bluetooth" in name or name.startswith("vEthernet"):
                    continue
                    
                ip = "No IP"
                for addr in addr_list:
                    if addr.family == socket.AF_INET:
                        ip = addr.address
                        break
                        
                is_up = stats.get(name, None)
                if is_up and not is_up.isup:
                    continue
                    
                display = name
                if ip != "No IP":
                    if ip == "127.0.0.1":
                        display += " (Loopback)"
                    else:
                        display += f" ({ip})"
                else:
                    display += " (No IP)"
                    
                has_ip = ip != "No IP" and ip != "127.0.0.1"
                is_loopback = ip == "127.0.0.1"
                
                results.append({
                    "id": name,
                    "display": display,
                    "has_ip": has_ip,
                    "is_loopback": is_loopback
                })
                
            results.sort(key=lambda x: (not x["has_ip"], x["is_loopback"], x["display"]))
            
            for r in results:
                del r["has_ip"]
                del r["is_loopback"]
                
            return results
        except Exception as e:
            return [{"id": "error", "display": f"Error: {e}"}]

    def start(self, interface: str):
        if self.is_running:
            return
            
        # Reset counters for the new session
        self.stats["packets_observed"] = 0
        self.stats["flows_observed"] = 0
        self.stats["alerts_generated"] = 0
        self.stats["recent_alerts"] = []
        
        # Dynamically resolve friendly name to UUID safely using subprocess
        target_uuid = None
        try:
            import subprocess
            cmd = f'Get-CimInstance Win32_NetworkAdapter | Where-Object {{ $_.Name -match "{interface}" -or $_.NetConnectionID -eq "{interface}" }} | Select-Object -ExpandProperty GUID -First 1'
            out = subprocess.check_output(["powershell", "-Command", cmd], text=True, timeout=5).strip()
            if out and out.startswith("{"):
                target_uuid = f"\\Device\\NPF_{out}"
        except Exception as e:
            print(f"Failed to resolve GUID for {interface}: {e}")
            
        if not target_uuid:
            # Fallback for loopback or unresolvable
            if "Loopback" in interface or interface == "Loopback Pseudo-Interface 1":
                target_uuid = "\\Device\\NPF_Loopback"
            else:
                self.stats["status"] = "ERROR"
                self.stats["error"] = f"Capture failed: Interface '{interface}' could not be resolved to a physical UUID."
                return
            
        print(f"Resolved frontend interface '{interface}' to target UUID: {target_uuid}")
        self.interface = target_uuid
        self.is_running = True
        self.stats["status"] = "ACTIVE"
        self.stats["error"] = None
        self.scapy_loaded = False
        
        self.thread = threading.Thread(target=self._capture_loop)
        self.thread.daemon = True
        self.thread.start()

        def watcher():
            time.sleep(8)
            if not getattr(self, "scapy_loaded", False) and self.is_running:
                self.stats["status"] = "ERROR"
                self.stats["error"] = "Npcap driver is deadlocked at OS level or requires Administrator privileges. Initialization timed out."
                self.is_running = False
                
        threading.Thread(target=watcher, daemon=True).start()

        self.proc_thread = threading.Thread(target=self._processing_loop)
        self.proc_thread.daemon = True
        self.proc_thread.start()

    def stop(self):
        self.is_running = False
        self.stats["status"] = "STOPPED"

    def _packet_handler(self, packet):
        if not self.is_running:
            return
        self.stats["packets_observed"] += 1
        with self.lock:
            self.buffer.append(packet)

    def _capture_loop(self):
        try:
            from scapy.all import sniff
            self.scapy_loaded = True
            sniff(iface=self.interface, prn=self._packet_handler, store=False, stop_filter=lambda p: not self.is_running)
        except Exception as e:
            self.stats["status"] = "ERROR"
            self.stats["error"] = f"Capture failed: {str(e)}. Check administrator permissions/Npcap."
            self.is_running = False
            
    def _processing_loop(self):
        while self.is_running:
            time.sleep(5)
            with self.lock:
                if not self.buffer:
                    continue
                packets_to_process = self.buffer[:]
                self.buffer.clear()
            try:
                self._process_window(packets_to_process)
            except Exception as e:
                print(f"Error processing live window: {e}")

    def _process_window(self, packets):
        events = parse_packets_to_events(packets)
        if not events: return
        df = create_flow_features(events)
        if df.empty: return
        self.stats["flows_observed"] += len(df)
        
        df_rules = evaluate_rules(df)
        df = pd.concat([df, df_rules], axis=1)
        
        df_ml = self.ml_engine.analyze_flows(df)
        df = pd.concat([df, df_ml], axis=1)
        
        df_risk = df.apply(calculate_risk, axis=1)
        df = pd.concat([df, df_risk], axis=1)
        
        alerts_created = []
        db = SessionLocal()
        try:
            import math
            def safe_float(v):
                try:
                    f = float(v)
                    return 0.0 if math.isnan(f) else f
                except:
                    return 0.0

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
                        risk_score=safe_float(row['final_risk_score']),
                        confidence=safe_float(row.get('rf_probability', 0.0)),
                        model_used="Rules+ML",
                        anomaly_score=safe_float(row.get('if_score', 0.0)),
                        evidence=row['evidence']
                    )
                    db.add(alert)
                    db.flush()
                    
                    self.stats["recent_alerts"].insert(0, {
                        "id": alert.id,
                        "timestamp": pd.Timestamp.utcnow().isoformat(),
                        "source_ip": alert.source_ip,
                        "destination_ip": alert.destination_ip,
                        "source_port": alert.source_port,
                        "destination_port": alert.destination_port,
                        "protocol": alert.protocol,
                        "threat_type": alert.threat_type,
                        "severity": alert.severity,
                        "risk_score": alert.risk_score
                    })
                    alerts_created.append(alert)
                    
            db.commit()
            self.stats["alerts_generated"] += len(alerts_created)
            self.stats["recent_alerts"] = self.stats["recent_alerts"][:10]
        finally:
            db.close()

live_capture_service = LiveCapture()
