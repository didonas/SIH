from scapy.all import sniff, conf
import urllib.request
import threading
import time
import socket

conf.use_npcap = True

def generate_traffic():
    time.sleep(1)
    try:
        urllib.request.urlopen("http://8.8.8.8", timeout=2)
    except:
        pass

packets = []
def cb(p):
    packets.append(p)

t = threading.Thread(target=generate_traffic)
t.start()

print("Sniffing on all interfaces with conf.use_npcap = True...")
sniff(prn=cb, timeout=5)
print(f"Captured {len(packets)} packets total.")
