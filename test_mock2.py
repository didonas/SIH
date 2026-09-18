import sys
from unittest.mock import MagicMock
sys.modules['scapy.interfaces'] = MagicMock()

from scapy.utils import rdpcap
try:
    packets = rdpcap('test_traffic/syn_flood/syn_flood.pcap')
    print("Parsed packets:", len(packets))
except Exception as e:
    print("Error parsing:", e)
