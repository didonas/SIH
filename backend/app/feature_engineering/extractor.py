import pandas as pd
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
