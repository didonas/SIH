import os
import json
import subprocess
from typing import List, Optional
from app.schemas.event import NormalizedEvent

def parse_packets_to_events(packets) -> List[NormalizedEvent]:
    from scapy.all import IP, TCP, UDP
    events = []
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
                ingestion_source="Passive_Live"
            )
            events.append(event)
    return events

def parse_pcap_to_events(filepath: str) -> Optional[List[NormalizedEvent]]:
    if not os.path.exists(filepath):
        return None
        
    worker_path = os.path.join(os.path.dirname(__file__), "pcap_worker.py")
    
    try:
        # Run the isolated worker to parse the PCAP using Scapy safely
        result = subprocess.run(
            ["python", worker_path, filepath], 
            capture_output=True, 
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            return None
            
        data = json.loads(result.stdout)
        if "error" in data:
            return None
            
        events = []
        for d in data.get("events", []):
            events.append(NormalizedEvent(**d))
        return events
    except subprocess.TimeoutExpired:
        raise TimeoutError("PCAP processing timed out. The file may be too large to process synchronously.")
    except Exception as e:
        return None
