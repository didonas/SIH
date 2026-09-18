import os

files = {
    'backend/app/feature_engineering/extractor.py': '''import pandas as pd
from collections import defaultdict
from scapy.all import rdpcap, IP, TCP, UDP, DNS

def extract_features_from_pcap(pcap_path):
    packets = rdpcap(pcap_path)
    flows = defaultdict(list)
    
    # Group by 5-tuple flow
    for pkt in packets:
        if IP in pkt:
            src = pkt[IP].src
            dst = pkt[IP].dst
            proto = pkt[IP].proto
            sport = 0
            dport = 0
            if TCP in pkt:
                sport = pkt[TCP].sport
                dport = pkt[TCP].dport
            elif UDP in pkt:
                sport = pkt[UDP].sport
                dport = pkt[UDP].dport
            
            flow_key = (src, dst, sport, dport, proto)
            flows[flow_key].append(pkt)
            
    # Calculate features for each flow
    features_list = []
    for flow_key, pkts in flows.items():
        src, dst, sport, dport, proto = flow_key
        
        packet_count = len(pkts)
        byte_count = sum(len(p) for p in pkts)
        
        if packet_count > 1:
            duration = float(pkts[-1].time - pkts[0].time)
        else:
            duration = 0.0001
            
        if duration <= 0:
            duration = 0.0001
            
        packets_per_second = packet_count / duration
        bytes_per_second = byte_count / duration
        
        # TCP Flags
        syn_count = 0
        ack_count = 0
        if proto == 6: # TCP
            for p in pkts:
                if TCP in p:
                    flags = p[TCP].flags
                    if 'S' in flags: syn_count += 1
                    if 'A' in flags: ack_count += 1
                    
        features = {
            'source_ip': src,
            'destination_ip': dst,
            'source_port': sport,
            'destination_port': dport,
            'protocol': 'TCP' if proto == 6 else 'UDP' if proto == 17 else str(proto),
            'packet_count': packet_count,
            'byte_count': byte_count,
            'duration': duration,
            'packets_per_second': packets_per_second,
            'bytes_per_second': bytes_per_second,
            'syn_count': syn_count,
            'ack_count': ack_count,
            'syn_ratio': syn_count / packet_count if packet_count > 0 else 0
        }
        features_list.append(features)
        
    return pd.DataFrame(features_list)
''',
    'backend/app/ml/engine.py': '''import joblib
import os
import pandas as pd
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), '../../../models')

class MLEngine:
    def __init__(self):
        self.rf_model = None
        self.if_model = None
        self.features = ['packet_count', 'byte_count', 'duration', 'packets_per_second', 'bytes_per_second', 'syn_count', 'syn_ratio']
        self.load_models()

    def load_models(self):
        rf_path = os.path.join(MODEL_DIR, 'random_forest.pkl')
        if_path = os.path.join(MODEL_DIR, 'isolation_forest.pkl')
        
        if os.path.exists(rf_path):
            self.rf_model = joblib.load(rf_path)
        if os.path.exists(if_path):
            self.if_model = joblib.load(if_path)

    def analyze_flows(self, df):
        if self.rf_model is None or self.if_model is None:
            # Fallback for demo if models not trained yet
            return self._heuristic_analysis(df)
            
        X = df[self.features].fillna(0)
        
        rf_preds = self.rf_model.predict(X)
        if_preds = self.if_model.predict(X) # 1 normal, -1 anomaly
        
        results = []
        for i, row in df.iterrows():
            threat = rf_preds[i] if isinstance(rf_preds[i], str) else 'NORMAL'
            anomaly = if_preds[i] == -1
            
            risk_score = 0
            severity = 'LOW'
            if anomaly: risk_score += 40
            if threat != 'NORMAL': risk_score += 50
            
            if risk_score > 80: severity = 'CRITICAL'
            elif risk_score > 60: severity = 'HIGH'
            elif risk_score > 30: severity = 'MEDIUM'
            
            res = {
                'threat_type': threat if threat != 'NORMAL' else ('ANOMALY' if anomaly else 'NORMAL'),
                'severity': severity,
                'risk_score': risk_score,
                'confidence': 0.85, # dummy confidence
                'anomaly_score': 0.9 if anomaly else 0.1,
                'evidence': {
                    'packets_per_second': row['packets_per_second'],
                    'syn_ratio': row.get('syn_ratio', 0)
                }
            }
            results.append(res)
            
        df_results = pd.DataFrame(results)
        return pd.concat([df.reset_index(drop=True), df_results], axis=1)

    def _heuristic_analysis(self, df):
        results = []
        for i, row in df.iterrows():
            threat = 'NORMAL'
            risk_score = 10
            evidence = {}
            
            # Simple heuristic for SYN flood
            if row.get('syn_ratio', 0) > 0.8 and row.get('packets_per_second', 0) > 100:
                threat = 'SYN_FLOOD'
                risk_score = 85
                evidence['reason'] = 'High SYN ratio and packet rate'
            
            # Simple heuristic for UDP Flood / DDoS
            elif row['protocol'] == 'UDP' and row['packets_per_second'] > 500:
                threat = 'UDP_FLOOD'
                risk_score = 90
                evidence['reason'] = 'Extremely high UDP packet rate'
                
            severity = 'LOW'
            if risk_score > 80: severity = 'CRITICAL'
            elif risk_score > 60: severity = 'HIGH'
            elif risk_score > 30: severity = 'MEDIUM'
            
            res = {
                'threat_type': threat,
                'severity': severity,
                'risk_score': risk_score,
                'confidence': 0.7,
                'anomaly_score': risk_score / 100.0,
                'evidence': evidence
            }
            results.append(res)
            
        df_results = pd.DataFrame(results)
        return pd.concat([df.reset_index(drop=True), df_results], axis=1)
'''
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
