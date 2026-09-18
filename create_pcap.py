from scapy.all import IP, TCP, wrpcap
import random
import time

packets = []
# Normal traffic
for i in range(10):
    p = IP(src="192.168.1.10", dst="10.0.0.5")/TCP(sport=random.randint(1024, 65535), dport=80, flags="PA")
    p.time = time.time() + i * 0.1
    packets.append(p)

# SYN Flood
for i in range(150):
    p = IP(src=f"10.1.1.{random.randint(1,250)}", dst="10.0.0.5")/TCP(sport=random.randint(1024, 65535), dport=80, flags="S")
    p.time = time.time() + 1 + i * 0.005
    packets.append(p)

wrpcap('test_traffic/syn_flood/syn_flood.pcap', packets)
print('Generated test PCAP')
