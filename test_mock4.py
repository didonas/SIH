import sys
from unittest.mock import patch

# We can mock pcap_findalldevs or load_winpcapy
import scapy.config
def fake_reload():
    pass

scapy.config.conf.ifaces = type('obj', (object,), {'reload': fake_reload})()

from scapy.all import rdpcap, IP
print("Success!")
