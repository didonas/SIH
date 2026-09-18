import sys
from unittest.mock import MagicMock
sys.modules['scapy.interfaces'] = MagicMock()

from scapy.utils import rdpcap
from scapy.layers.inet import IP, TCP
try:
    packets = rdpcap('test_traffic/syn_flood/syn_flood.pcap')
    print("Parsed packets:", len(packets))
    print("Has IP:", IP in packets[0])
except Exception as e:
    print("Error parsing:", e)
