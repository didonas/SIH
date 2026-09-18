import time
import sys

print("Testing direct sniff...")
try:
    # Set use_pcap to False before import to prevent pcap_findalldevs hang if possible? No, we need it.
    from scapy.all import sniff, IP, conf
    print("Scapy loaded.")
    
    iface = r'\Device\NPF_{FB358B94-E25B-41E1-8C4E-8293187EC68B}'
    print(f"Sniffing on {iface}...")
    pkts = sniff(iface=iface, count=3, timeout=5)
    print(f"Captured {len(pkts)} packets.")
except Exception as e:
    print(f"Error: {e}")
