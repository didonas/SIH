import json
from typing import List
from app.schemas.event import NormalizedEvent

def parse_zeek_conn_log(log_path: str) -> List[NormalizedEvent]:
    events = []
    try:
        with open(log_path, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                # Assuming TSV format for conn.log if not JSON
                # Actually, many Zeek deployments use JSON. Let's support JSON
                try:
                    data = json.loads(line)
                    event = NormalizedEvent(
                        timestamp=float(data.get('ts', 0)),
                        source_ip=data.get('id.orig_h', ''),
                        destination_ip=data.get('id.resp_h', ''),
                        source_port=int(data.get('id.orig_p', 0)),
                        destination_port=int(data.get('id.resp_p', 0)),
                        protocol=data.get('proto', ''),
                        packet_length=int(data.get('orig_bytes', 0)) + int(data.get('resp_bytes', 0)),
                        tcp_flags=data.get('history', ''),
                        ingestion_source='ZEEK'
                    )
                    events.append(event)
                except json.JSONDecodeError:
                    # Very basic TSV parsing fallback
                    parts = line.split('\t')
                    if len(parts) >= 21:
                        event = NormalizedEvent(
                            timestamp=float(parts[0]),
                            source_ip=parts[2],
                            destination_ip=parts[4],
                            source_port=int(parts[3]),
                            destination_port=int(parts[5]),
                            protocol=parts[6],
                            packet_length=int(parts[9] if parts[9].isdigit() else 0) + int(parts[10] if parts[10].isdigit() else 0),
                            tcp_flags=parts[16],
                            ingestion_source='ZEEK'
                        )
                        events.append(event)
    except FileNotFoundError:
        print(f"Zeek log {log_path} not found.")
    return events
