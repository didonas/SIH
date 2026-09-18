import pandas as pd
from typing import List
from app.schemas.event import NormalizedEvent
from collections import defaultdict

def create_flow_features(events: List[NormalizedEvent]):
    if not events:
        return pd.DataFrame()
        
    flows = defaultdict(list)
    for event in events:
        flow_key = (event.source_ip, event.destination_ip, event.source_port, event.destination_port, event.protocol)
        flows[flow_key].append(event)
        
    features_list = []
    for flow_key, evts in flows.items():
        src, dst, sport, dport, proto = flow_key
        
        packet_count = len(evts)
        byte_count = sum(e.packet_length for e in evts)
        
        start_time = min(e.timestamp for e in evts)
        end_time = max(e.timestamp for e in evts)
        duration = end_time - start_time
        if duration <= 0:
            duration = 0.0001
            
        if packet_count <= 1:
            packets_per_second = float(packet_count)
            bytes_per_second = float(byte_count)
        else:
            packets_per_second = packet_count / duration
            bytes_per_second = byte_count / duration
        
        syn_count = sum(1 for e in evts if e.tcp_flags and 'S' in e.tcp_flags)
        ack_count = sum(1 for e in evts if e.tcp_flags and 'A' in e.tcp_flags)
        
        features = {
            'source_ip': src,
            'destination_ip': dst,
            'source_port': sport,
            'destination_port': dport,
            'protocol': proto,
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
        
    df = pd.DataFrame(features_list)
    
    if not df.empty:
        df['unique_dst_ports'] = df.groupby(['source_ip', 'destination_ip'])['destination_port'].transform('nunique')
        df['dst_packet_count'] = df.groupby('destination_ip')['packet_count'].transform('sum')
        df['dst_syn_count'] = df.groupby('destination_ip')['syn_count'].transform('sum')
    else:
        df['unique_dst_ports'] = 0
        df['dst_packet_count'] = 0
        df['dst_syn_count'] = 0
        
    return df
