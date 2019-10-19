#!/usr/bin/python3
import socket
from colorama import init, Fore


# add color
init()
GREEN = Fore.GREEN
RESET = Fore.RESET
GRAY = Fore.LIGHTBLACK_EX


host = input("Ether the host: ")


def is_port_open(host, port):
    sock = socket.socket()
    try:
        sock.connect((host, port))
        sock.settimeout(0.5)
    except:
        return False
    else:
        return True
    finally:
        sock.close()


# iterate over ports, from 1 to 1024
for port in range(1, 1024):
    if is_port_open(host, port):
        print(f"{GREEN}[+] {host}:{port} is open        {RESET}")
    else:
        print(f"{GRAY}[!] {host}:{port} is closed       {RESET}", end='\r')
