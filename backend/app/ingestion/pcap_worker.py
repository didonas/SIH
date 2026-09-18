import sys
import json
import ctypes

# Mock ctypes to bypass Npcap deadlock on broken Windows adapters
original_load = ctypes.cdll.LoadLibrary
original_wload = getattr(ctypes, 'windll', None)

def fake_load(name, *args, **kwargs):
    if "wpcap" in str(name).lower():
        raise OSError("Bypassing Npcap for offline analysis")
    return original_load(name, *args, **kwargs)

def fake_wload(name, *args, **kwargs):
    if "wpcap" in str(name).lower():
        raise OSError("Bypassing Npcap for offline analysis")
    return original_wload.LoadLibrary(name, *args, **kwargs) if original_wload else original_load(name, *args, **kwargs)

ctypes.cdll.LoadLibrary = fake_load
if original_wload:
    ctypes.windll.LoadLibrary = fake_wload

# Now safe to import scapy without deadlocking on Npcap enumeration
from scapy.all import PcapReader, IP, TCP, UDP, ICMP

def process_pcap(filepath):
    events = []
    try:
        with PcapReader(filepath) as pcap_reader:
            count = 0
            for pkt in pcap_reader:
                count += 1
                if count > 10000:
                    break
                if IP in pkt:
                    event = {
                        "timestamp": float(pkt.time),
                        "source_ip": pkt[IP].src,
                        "destination_ip": pkt[IP].dst,
                        "protocol": "TCP" if TCP in pkt else "UDP" if UDP in pkt else "ICMP" if ICMP in pkt else str(pkt[IP].proto),
                        "source_port": int(pkt[TCP].sport) if TCP in pkt else int(pkt[UDP].sport) if UDP in pkt else 0,
                        "destination_port": int(pkt[TCP].dport) if TCP in pkt else int(pkt[UDP].dport) if UDP in pkt else 0,
                        "packet_length": len(pkt),
                        "tcp_flags": str(pkt[TCP].flags) if TCP in pkt else "",
                        "ingestion_source": "PCAP_Upload"
                    }
                    events.append(event)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    print(json.dumps({"events": events}))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_pcap(sys.argv[1])
