import os

files = {
    'backend/app/detection/rules.py': '''import pandas as pd

def evaluate_rules(df: pd.DataFrame):
    results = []
    for idx, row in df.iterrows():
        rule_threats = []
        rule_evidence = []
        rule_score = 0
        
        # Volumetric Flooding
        if row['packets_per_second'] > 500:
            rule_threats.append("VOLUMETRIC_FLOOD")
            rule_evidence.append(f"High packet rate: {row['packets_per_second']:.2f} pps")
            rule_score += 60
            
        # Reconnaissance / Port Scan (Simple proxy: lots of SYNs without ACKs or specific scanning behaviour)
        if row['protocol'] == 'TCP' and row.get('syn_ratio', 0) > 0.8 and row['packet_count'] > 10:
            rule_threats.append("POSSIBLE_SCAN_OR_SYN_FLOOD")
            rule_evidence.append(f"High SYN ratio: {row['syn_ratio']:.2f}")
            rule_score += 40
            
        results.append({
            'rule_threats': rule_threats,
            'rule_evidence': rule_evidence,
            'rule_score': min(rule_score, 100)
        })
    return pd.DataFrame(results, index=df.index)
''',
    'backend/app/detection/risk_scoring.py': '''def calculate_risk(row):
    score = 0
    evidence = []
    threat_type = "NORMAL"
    
    # Base score from rules
    if row.get('rule_score', 0) > 0:
        score += row['rule_score'] * 0.5
        evidence.extend(row.get('rule_evidence', []))
        if row.get('rule_threats'):
            threat_type = row['rule_threats'][0]
            
    # Score from Isolation Forest
    if row.get('if_anomaly', False):
        score += 40
        evidence.append("Isolation Forest detected anomalous behavior")
        if threat_type == "NORMAL":
            threat_type = "ANOMALY"
            
    # Score from Random Forest
    rf_pred = row.get('rf_prediction', 'NORMAL')
    if rf_pred != 'NORMAL':
        score += 50
        evidence.append(f"Random Forest classified as {rf_pred}")
        threat_type = rf_pred
        
    score = min(score, 100)
    
    severity = "LOW"
    if score >= 80:
        severity = "CRITICAL"
    elif score >= 60:
        severity = "HIGH"
    elif score >= 30:
        severity = "MEDIUM"
        
    return pd.Series({
        'final_threat_type': threat_type,
        'final_risk_score': score,
        'severity': severity,
        'evidence': evidence
    })
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

    def analyze_flows(self, df: pd.DataFrame):
        results = []
        if df.empty:
            return df
            
        # Ensure features exist
        for col in self.features:
            if col not in df.columns:
                df[col] = 0
                
        X = df[self.features].fillna(0)
        
        rf_preds = ["NORMAL"] * len(df)
        if self.rf_model:
            rf_preds = self.rf_model.predict(X)
            
        if_preds = [1] * len(df)
        if self.if_model:
            if_preds = self.if_model.predict(X)
            
        return pd.DataFrame({
            'rf_prediction': rf_preds,
            'if_anomaly': [p == -1 for p in if_preds]
        }, index=df.index)
'''
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
