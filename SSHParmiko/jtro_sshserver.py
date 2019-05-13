#!/usr/bin/python3
import sys
import socket
import paramiko
import threading


# using the key from paramikto demo files
host_key = paramiko.RSAKey(filename='public_rsa.key')


class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == 'jaki') and (password == 'pythonlover'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    server = sys.argv[1]
    ssh_port = int(sys.argv[2])
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))
        sock.listen(100)
        print("[+] Listening for connection...")
        client, addr = sock.accept()
    except Exception as e:
        print("[-] Listen faild: " + str(e))
        sys.exit(1)
    print("[+] Got a connection!")

    try:
        jt_session = paramiko.Transport(client)
        jt_session.add_server_key(host_key)
        server = Server()
        try:
            jt_session.start_server(server=server)
        except paramiko.SSHException as e:
            print("[-] SSH negotiation failed! " + str(e))
        chan = jt_session.accept(20)
        print("[+] Authenticated!")
        print(chan.recv(1024))
        chan.send('Welcome to JtroSSH')
        while True:
            try:
                command = input("Enter Command: ").strip('\n')
                if command != 'exit':
                    chan.send(command)
                    print(chan.recv(1024) + '\n')
                else:
                    chan.send('exit')
                    print('existing')
                    jt_session.close()
                    raise Exception('exit')
            except:
                jt_session.close()
    except Exception as e:
        print("[-] Exception. Code break! " + str(e))
        try:
            jt_session.close()
        except:
            pass
    sys.exit(1)
