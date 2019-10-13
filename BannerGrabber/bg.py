#!/usr/bin/python3
import socket


def CheckClosePort(ip, port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(5)
	return s.connect_ex((ip, port))


def banner(ip, port):
	sock = socket.socket()
	sock.connect((ip, port))
	sock.settimeout(5)
	print(sock.recv(1024))


def main():
	ip = input("IP: ")
	port = int(input("Port: "))
	if CheckClosePort(ip, port):
		print("The port is closed!")
	else:
		banner(ip, port)


if __name__ == "__main__": main()
