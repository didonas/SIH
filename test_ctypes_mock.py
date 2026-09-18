import sys
import ctypes

original_load = ctypes.cdll.LoadLibrary
original_wload = ctypes.windll.LoadLibrary

def fake_load(name, *args, **kwargs):
    if "wpcap" in str(name).lower():
        raise OSError("Simulated Npcap absence")
    return original_load(name, *args, **kwargs)

def fake_wload(name, *args, **kwargs):
    if "wpcap" in str(name).lower():
        raise OSError("Simulated Npcap absence")
    return original_wload(name, *args, **kwargs)

ctypes.cdll.LoadLibrary = fake_load
ctypes.windll.LoadLibrary = fake_wload

try:
    from scapy.all import rdpcap, IP
    packets = rdpcap('test_traffic/syn_flood/syn_flood.pcap')
    print("Success! Parsed", len(packets), "packets. Has IP:", IP in packets[0])
except Exception as e:
    print("Error:", e)
