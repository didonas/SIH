import pandas as pd

def calculate_risk(row):
    score = 0
    evidence = []
    threat_type = "NORMAL"
    
    # Extract real factual features to include in evidence if there is a threat
    packet_count = row.get('packet_count', 0)
    syn_ratio = row.get('syn_ratio', 0.0)
    rf_prob = row.get('rf_probability', 0.0)
    if_score = row.get('if_score', 0.0)

    # Base score from rules
    rule_s = row.get('rule_score', 0)
    if rule_s > 0:
        # Using the rule score directly. (The 0.5 was a weight in the prototype, let's keep the formula but make it clear)
        score += rule_s * 0.5 
        evidence.extend(row.get('rule_evidence', []))
        if row.get('rule_threats'):
            threat_type = row['rule_threats'][0]
            
    # Score from Isolation Forest
    if row.get('if_anomaly', False):
        score += 40
        evidence.append(f"Isolation Forest score: {if_score}")
        if threat_type == "NORMAL":
            threat_type = "ANOMALY"
            
    # Score from Random Forest
    rf_pred = row.get('rf_prediction', 'NORMAL')
    if rf_pred != 'NORMAL':
        score += 50
        evidence.append(f"Random Forest prediction: {rf_pred} (Probability: {rf_prob:.2f})")
        threat_type = rf_pred
        
    import math
    if pd.isna(score) or math.isnan(score) or math.isinf(score):
        score = 0
    score = max(0, min(float(score), 100))
    
    # Only append raw metrics if risk > 0 (meaning we are alerting)
    if score > 0:
        evidence.append(f"Flow packet count: {packet_count}")
        evidence.append(f"Flow SYN ratio: {syn_ratio:.2f}")
    
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
