import time
import sys
import ctypes

old_load = ctypes.cdll.LoadLibrary
def safe_load(name, *args, **kwargs):
    if "wpcap" in name.lower():
        raise OSError("Monkey-patched wpcap failure to bypass deadlock")
    return old_load(name, *args, **kwargs)
ctypes.cdll.LoadLibrary = safe_load

from scapy.all import sniff, IP, conf

print("Scapy loaded without pcap.")
try:
    print("Sniffing via raw sockets (conf.use_pcap = False)...")
    pkts = sniff(count=1, timeout=5)
    print(f"Captured {len(pkts)} packets.")
except Exception as e:
    print(f"Error: {e}")
