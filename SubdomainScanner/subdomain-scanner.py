#!/bin/usr/python3
import requests


domain = input("Target Domain: ")
file = open("subdomain.txt")
content = file.read()
subdomains = content.splitlines()


for subdomains in subdomains:
    url = f"http://{subdomains}.{domain}"
    try:
        requests.get(url)
    except requests.ConnectionError:
        pass
    else:
        print("[+] Discover URL: ", url)
