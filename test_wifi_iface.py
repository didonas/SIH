from scapy.all import conf

for i in conf.ifaces.values():
    if "Wi-Fi 6 AX200" in getattr(i, "description", "") or getattr(i, "ip", "") == "10.228.3.220":
        print(getattr(i, "network_name", ""))
