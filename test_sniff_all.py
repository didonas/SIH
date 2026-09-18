from scapy.all import sniff, conf
import urllib.request
import threading
import time

def generate_traffic():
    time.sleep(1)
    try:
        urllib.request.urlopen("http://example.com", timeout=2)
    except:
        pass

packets = []
def cb(p):
    packets.append(p)

t = threading.Thread(target=generate_traffic)
t.start()

print("Sniffing on all interfaces...")
sniff(prn=cb, timeout=5)
print(f"Captured {len(packets)} packets total.")
if packets:
    print(f"First packet summary: {packets[0].summary()}")
