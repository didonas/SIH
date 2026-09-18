import ctypes
from ctypes import *
import time

wpcap = CDLL("wpcap.dll")

# int pcap_findalldevs(pcap_if_t **alldevsp, char *errbuf);
wpcap.pcap_findalldevs.restype = c_int
wpcap.pcap_findalldevs.argtypes = [POINTER(c_void_p), c_char_p]

errbuf = create_string_buffer(256)
alldevs = c_void_p()

print("Calling pcap_findalldevs...")
start = time.time()
try:
    res = wpcap.pcap_findalldevs(byref(alldevs), errbuf)
    print(f"Result: {res}, Time: {time.time()-start:.2f}s")
except Exception as e:
    print(e)
