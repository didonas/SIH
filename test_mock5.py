import sys
import unittest.mock

# intercept scapy.arch.windows before it loads
import scapy.arch.windows
scapy.arch.windows.load_winpcapy = lambda: None
scapy.arch.windows.get_windows_if_list = lambda: []

from scapy.all import rdpcap, IP
print("Success!")
