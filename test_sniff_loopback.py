from scapy.all import sniff, conf
import threading
import time
import os

target = r"\Device\NPF_{11D4E58E-EF01-4358-BF17-1FC9DCB9075C}" # Just an example, let's look up Loopback
for i in conf.ifaces.values():
    if "Loopback" in getattr(i, "description", "") or "Loopback" in getattr(i, "name", ""):
        target = getattr(i, "network_name", "")
        print(f"Found Loopback: {target}")
        break

def generate_traffic():
    time.sleep(1)
    os.system("ping 127.0.0.1 -n 2 > nul")

packets = []
def cb(p):
    packets.append(p)

t = threading.Thread(target=generate_traffic)
t.start()

print(f"Sniffing on {target} ...")
sniff(iface=target, prn=cb, timeout=5)
print(f"Captured {len(packets)} packets total on Loopback.")
