from scapy.all import IP, TCP, wrpcap
import random
import time
import os

packets = []
start_time = time.time()
src_ip = "10.0.0.99"
dst_ip = "192.168.1.100"

# Target 100 random ports to trigger the unique_dst_ports > 15 rule
target_ports = random.sample(range(1, 1024), 100)

for i, dport in enumerate(target_ports):
    # Send SYN
    p = IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(10000, 60000), dport=dport, flags="S")
    p.time = start_time + (i * 0.01) # Scan at 100 packets per second
    packets.append(p)

os.makedirs("test_traffic/port_scan", exist_ok=True)
wrpcap("test_traffic/port_scan/port_scan.pcap", packets)
print(f"Generated {len(packets)} packets targeting {len(target_ports)} unique ports in test_traffic/port_scan/port_scan.pcap")
