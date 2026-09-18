from scapy.all import sniff, conf
import threading
import urllib.request
import time

target = None
for i in conf.ifaces.values():
    if getattr(i, "ip", "") == "10.214.224.222":
        target = getattr(i, "network_name", "")
        print(f"Found active internet adapter: {getattr(i, 'name', '')} ({target})")
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

if target:
    print(f"Sniffing on {target} ...")
    sniff(iface=target, prn=cb, timeout=5)
    print(f"Captured {len(packets)} packets total on active adapter.")
