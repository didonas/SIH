import sys
from unittest.mock import MagicMock

# Mock scapy.interfaces to prevent reload()
sys.modules['scapy.interfaces'] = MagicMock()

try:
    from scapy.utils import rdpcap
    print("Success without interface enumeration!")
except Exception as e:
    print("Error:", e)
