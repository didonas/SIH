import os

files = {
    'backend/app/schemas/event.py': '''from pydantic import BaseModel
from typing import Optional

class NormalizedEvent(BaseModel):
    timestamp: float
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    packet_length: int
    tcp_flags: Optional[str] = None
    ingestion_source: str = "PCAP"
''',
    'backend/app/ingestion/pcap_adapter.py': '''from scapy.all import rdpcap, IP, TCP, UDP
from app.schemas.event import NormalizedEvent

def parse_pcap_to_events(pcap_path: str):
    events = []
    packets = rdpcap(pcap_path)
    
    for pkt in packets:
        if IP in pkt:
            src = pkt[IP].src
            dst = pkt[IP].dst
            proto = pkt[IP].proto
            length = len(pkt)
            timestamp = float(pkt.time)
            
            sport = 0
            dport = 0
            flags = None
            protocol_name = str(proto)
            
            if TCP in pkt:
                sport = pkt[TCP].sport
                dport = pkt[TCP].dport
                flags = str(pkt[TCP].flags)
                protocol_name = 'TCP'
            elif UDP in pkt:
                sport = pkt[UDP].sport
                dport = pkt[UDP].dport
                protocol_name = 'UDP'
                
            event = NormalizedEvent(
                timestamp=timestamp,
                source_ip=src,
                destination_ip=dst,
                source_port=sport,
                destination_port=dport,
                protocol=protocol_name,
                packet_length=length,
                tcp_flags=flags,
                ingestion_source="PCAP_Scapy"
            )
            events.append(event)
            
    return events
''',
    'backend/app/feature_engineering/window_engine.py': '''import pandas as pd
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
        
    return pd.DataFrame(features_list)
'''
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
