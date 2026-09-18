from pydantic import BaseModel
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
