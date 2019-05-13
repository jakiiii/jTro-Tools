#!/usr/bin/python3
"""
Sniffer IP Header Decode
"""
import os
import struct
import socket
from ctypes import *


# host to listen
host = "192.168.31.34"


# IP header
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


if os.name == 'nt':
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP


sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0))
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

if os.name == 'nt':
    sniffer.ioctl((socket.SIO_RCVALL, socket.RCVALL_ON))

try:
    while True:
        # read packet
        raw_buffer = sniffer.recvfrom(65565)[0]

        # create IP header from the first 10 bytes of the buffer
        ip_header = IP(raw_buffer[0:20])

        # print out protocol that was detected and the hosts
        print("Protocol: {} {} -> {}".format(ip_header.protocol, ip_header.src_address, ip_header.dst_address))
# handle CRTL-C
except KeyboardInterrupt:
    # is os is windows, turn off promiscuous mode
    if os.name == 'nt':
        sniffer.ioctl((socket.SIO_RCVALL, socket.RCVALL_OFF))
