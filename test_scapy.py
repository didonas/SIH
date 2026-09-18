import sys
import time

try:
    print("Importing scapy...")
    t0 = time.time()
    from scapy.all import conf
    t1 = time.time()
    print(f"Imported scapy in {t1-t0:.2f}s")
    
    print("Enumerating interfaces...")
    print(conf.ifaces)
    t2 = time.time()
    print(f"Enumerated interfaces in {t2-t1:.2f}s")
    
except Exception as e:
    print(f"Error: {e}")
