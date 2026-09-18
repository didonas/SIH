import ctypes
import time
import sys

try:
    wpcap = ctypes.cdll.LoadLibrary("wpcap.dll")
    print("Loaded wpcap.dll")
    
    errbuf = ctypes.create_string_buffer(256)
    
    # Try pcap_findalldevs
    print("Calling pcap_findalldevs_ex...")
    alldevs = ctypes.POINTER(ctypes.c_void_p)()
    # PCAP_SRC_IF_STRING is "rpcap://"
    res = wpcap.pcap_findalldevs_ex(b"rpcap://", None, ctypes.byref(alldevs), errbuf)
    print(f"Result: {res}")
    if res != 0:
        print(f"Error: {errbuf.value.decode()}")
except Exception as e:
    print(f"Exception: {e}")
