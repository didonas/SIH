import pandas as pd

def evaluate_rules(df: pd.DataFrame):
    results = []
    for idx, row in df.iterrows():
        rule_threats = []
        rule_evidence = []
        rule_score = 0
        
        # Volumetric Flooding
        if row.get('dst_packet_count', 0) > 200:
            rule_threats.append("VOLUMETRIC_FLOOD")
            rule_evidence.append(f"Destination targeted by {row['dst_packet_count']} packets in window")
            rule_score += 60
            
        # Reconnaissance / Port Scan
        if row.get('unique_dst_ports', 0) > 15:
            rule_threats.append("PORT_SCAN_RECONNAISSANCE")
            rule_evidence.append(f"Source scanned {row['unique_dst_ports']} unique ports on destination")
            rule_score += 75
            
        # SYN Flood / Half-open
        if row['protocol'] == 'TCP' and row.get('dst_syn_count', 0) > 50:
            rule_threats.append("POSSIBLE_SYN_FLOOD")
            rule_evidence.append(f"Destination targeted by {row['dst_syn_count']} SYN packets in window")
            rule_score += 60
            
        results.append({
            'rule_threats': rule_threats,
            'rule_evidence': rule_evidence,
            'rule_score': min(rule_score, 100)
        })
    return pd.DataFrame(results, index=df.index)
