import time
t0 = time.time()
from scapy.layers.inet import IP
print(f"Loaded IP in {time.time()-t0:.2f}s")
