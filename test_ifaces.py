from scapy.all import conf
for i in conf.ifaces.values():
    print(f'NAME: {i.name}')
    print(f'DESC: {getattr(i, "description", "")}')
    print(f'IP: {getattr(i, "ip", "")}')
    print('---')
