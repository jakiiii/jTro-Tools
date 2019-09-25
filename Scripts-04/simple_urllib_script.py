#!/usr/bin/python3
import urllib.request


# url = "https://twitter.com/"
url = "https://nostarch.com/"

headers = {}
headers['User-Agent'] = "Googlebot"

request = urllib.request.Request(url, headers=headers)
response = urllib.request.urlopen(request)

print(response.read().decode('utf-8'))
response.close()
