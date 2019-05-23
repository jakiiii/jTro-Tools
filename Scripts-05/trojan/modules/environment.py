#!/usr/bin/python3
import os


def run(**args):
    print("[+] In enviroment module.")
    return str(os.environ)
