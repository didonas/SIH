from scapy.all import IP, TCP, wrpcap
import random
import time

packets = []
start_time = time.time()

# 1. Normal HTTP traffic (low volume, completed handshakes, longer duration)
# 50 normal flows
for flow_id in range(50):
    src_ip = f"192.168.1.{random.randint(10, 50)}"
    dst_ip = "10.0.0.10"
    src_port = random.randint(10000, 60000)
    dst_port = 80
    
    # 5-10 packets per flow
    for i in range(random.randint(5, 10)):
        p = IP(src=src_ip, dst=dst_ip)/TCP(sport=src_port, dport=dst_port, flags="A")
        p.time = start_time + flow_id * 0.1 + i * 0.05
        packets.append(p)

# 2. SYN Flood (high volume, all SYN, same dst_port, random src_ports)
# 150 malicious packets (each creates a 1-packet flow in our naive 5-tuple windowing since port changes)
flood_start = start_time + 10
for i in range(150):
    src_ip = f"10.0.0.{random.randint(100, 200)}"
    dst_ip = "192.168.1.5"
    src_port = random.randint(1024, 65535)
    
    p = IP(src=src_ip, dst=dst_ip)/TCP(sport=src_port, dport=80, flags="S")
    p.time = flood_start + i * 0.005 # very fast
    packets.append(p)

# Sort by time
packets.sort(key=lambda x: x.time)
wrpcap("mixed_traffic.pcap", packets)
print(f"Generated {len(packets)} packets in mixed_traffic.pcap")
