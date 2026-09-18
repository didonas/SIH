import ctypes
import time

try:
    wpcap = ctypes.cdll.LoadLibrary("wpcap.dll")
    print("Loaded wpcap.dll")
    
    errbuf = ctypes.create_string_buffer(256)
    
    # Try pcap_open_live
    iface = b"\\Device\\NPF_{FB358B94-E25B-41E1-8C4E-8293187EC68B}"
    print(f"Calling pcap_open_live on {iface}...")
    
    wpcap.pcap_open_live.restype = ctypes.c_void_p
    handle = wpcap.pcap_open_live(iface, 65536, 1, 1000, errbuf)
    
    if not handle:
        print(f"Error: {errbuf.value.decode()}")
    else:
        print("Success! handle opened.")
        wpcap.pcap_close(ctypes.c_void_p(handle))
except Exception as e:
    print(f"Exception: {e}")
