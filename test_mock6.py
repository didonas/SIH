import sys

# Pre-load scapy.arch.libpcap and mock it before scapy.all is imported
import scapy.arch.libpcap
scapy.arch.libpcap.load_winpcapy = lambda *args, **kwargs: None

from scapy.all import rdpcap, IP
print("Success!")
