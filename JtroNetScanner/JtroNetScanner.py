#!/usr/bin/python3
from scapy.all import ARP, Ether, srp


target_ip = input("Target IP/Destination\nE.g. 192.162.0.0/24\n")

# print(type(target_ip))

# create ARP packet
arp = ARP(pdst=target_ip)
# create Ether broadcast packet
ether = Ether(dst="ff:ff:ff:ff:ff:ff")

# stack them
packet = ether/arp

result = srp(packet, timeout=3)[0]

clients = []

for sent, receive in result:
    clients.append({'ip': receive.psrc, 'mac': receive.hwsrc})

print("Available device in the network:")
print("IP" + " "*19 + "MAC")
for client in clients:
    print("{:16}     {}".format(client['ip'], client['mac']))
