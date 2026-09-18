import ctypes
wpcap = ctypes.cdll.LoadLibrary("wpcap.dll")
errbuf = ctypes.create_string_buffer(256)
iface = b"\\Device\\NPF_Loopback"
wpcap.pcap_open_live.restype = ctypes.c_void_p
handle = wpcap.pcap_open_live(iface, 65536, 1, 1000, errbuf)
if handle:
    print("Loopback opened successfully!")
else:
    print("Loopback failed:", errbuf.value.decode())
