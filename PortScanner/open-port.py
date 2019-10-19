#!/usr/bin/python3
import sys
import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)

host = input("IP: ")
port = int(input("Port: "))


def PortScanner(port):
	if sock.connect_ex((host, port)):
		print("The Port is closed!")
	else:
		print("Port is open")


PortScanner(port)
