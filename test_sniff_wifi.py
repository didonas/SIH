from scapy.all import sniff, conf
import threading
import urllib.request
import time

target_iface_name = r"\Device\NPF_{FB358B94-E25B-41E1-8C4E-8293187EC68B}"
found_iface = None
for i in conf.ifaces.values():
    if getattr(i, "network_name", "") == target_iface_name:
        found_iface = i
        break

packets = []
def cb(p):
    packets.append(p)

def generate_traffic():
    time.sleep(1)
    try:
        urllib.request.urlopen("http://example.com", timeout=2)
    except:
        pass

t = threading.Thread(target=generate_traffic)
t.start()

print("Sniffing on Wi-Fi with promisc=False...")
sniff(iface=target_iface_name, prn=cb, timeout=5, promisc=False)
print(f"Captured {len(packets)} packets.")
