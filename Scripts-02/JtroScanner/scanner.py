#!/usr/bin/python3
import os
import time
import struct
import socket
import threading

from ctypes import *
from netaddr import IPAddress, IPNetwork


# host to listen
host = "192.168.31.34"

# subnet to target
subnet = "192.168.31.0/24"

# magic string for checking ICMP response
magic_message = "PYTHONLOVER!"


# spray out the UDP datagrams
def udp_sender(subnet, magic_message):
    time.sleep(5)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for ip in IPNetwork(subnet):
        try:
            sender.sendto(magic_message, ("{}".format(ip), 65212))
        except:
            pass


class IP(Structure):
    _fields_ = [
        ("ihl", c_ubyte, 4),
        ("version", c_ubyte, 4),
        ("tos", c_ubyte, 8),
        ("len", c_ushort, 16),
        ("id", c_ushort, 16),
        ("offset", c_ushort, 16),
        ("ttl", c_ubyte, 8),
        ("protocol_num", c_ubyte, 8),
        ("sum", c_ushort, 16),
        ("src", c_uint, 32),
        ("dst", c_uint, 32),
    ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        # map protocol contains to their names
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # human readable IP address
        self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))
        # self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        # self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))

        # human readable protocol
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)


class ICMP(Structure):
    _fields = [
        ("type", c_ubyte, 4),
        ("code", c_ubyte, 4),
        ("checksum", c_ushort, 16),
        ("unused", c_ushort, 16),
        ("next_hop_mtu", c_ushort, 16),
    ]

    def __new__(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass


# create raw socket and bind it to the public interface
if os.name == 'nt':
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP


sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0))
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

if os.name == 'nt':
    sniffer.ioctl((socket.SIO_RCVALL, socket.RCVALL_ON))


# start sending packets
th = threading.Thread(target=udp_sender, args=(subnet, magic_message))
th.start()

try:
    while True:
        # read single packet
        raw_buffer = sniffer.recvfrom(65565)[0]

        # create IP header first 20 bytes of the buffer
        ip_header = IP(raw_buffer[0:20])

        # print("{} {} -> {}".format(ip_header.protocol, ip_header.src_address, ip_header.dst_address))

        # for ICMP
        if ip_header.protocol == "ICMP":
            # calculate where ICMP packet starts
            offset = ip_header.ihl * 4
            buf = raw_buffer[offset:offset + sizeof(ICMP)]

            # ICMP structure
            icmp_header = ICMP(buf)

            # print("ICMP -> Type: {} code: {}".format(icmp_header.type, icmp_header.code))
            # check for the TYPE 3 and CODE 3
            if icmp_header.code == 3 and icmp_header.type == 3:
                # make sure host is in our target subnet
                if IPAddress(ip_header.src_address) in IPNetwork(subnet):
                    # make sure the magic message
                    if raw_buffer[len(raw_buffer) - len(magic_message):] == magic_message:
                        print("Host Up: {}".format(ip_header.src_address))
except KeyboardInterrupt:
    # is os is windows, turn off promiscuous mode
    if os.name == 'nt':
        sniffer.ioctl((socket.SIO_RCVALL, socket.RCVALL_OFF))
