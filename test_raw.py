import time
t0 = time.time()
from scapy.utils import RawPcapReader
print(f"Loaded RawPcapReader in {time.time()-t0:.2f}s")
