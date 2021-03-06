#!/usr/bin/python3
"""
jTro proxy is like TCP Proxy. This script is learning purpose and we used BLACK HAT PYTHON
book by Justin Seitz's script.

This script in a number of cases to help understand unknown protocols, modify traffic being send to an application,
and create test cases for fuzzers.
"""
import sys
import socket
import threading


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except socket.error as e:
        print("[!!] Failed to listen on {}:{}".format(local_host, local_port) + str(e))
        print("[!!] Check for other listening or correct permissions.")
        sys.exit()

    print("[+] Listening on {}:{}".format(local_host, local_port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # print out the local connection information
        print("[-->] Received incoming connection from {}:{}".format(addr[0], addr[1]))

        # start thread to talk to the remote host
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host,
                                                                    remote_port, receive_first))
        proxy_thread.start()


def proxy_handler(client_socket, remote_hsot, remote_port, receive_first):
    # connect to the remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_hsot, remote_port))

    # receive data from the remote end if necessary
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        # send it to response handler
        remote_buffer = response_handler(remote_buffer)

        # if we have data to send to our local client
        if len(remote_buffer):
            print("[<==] Sending %d bytes to localhost. {}".format(len(remote_buffer)))
            client_socket.send(remote_buffer)

        # read data from local, send remote and send local
        # rinse, wash, repeat
        while True:
            # read from localhost
            local_buffer = receive_from(client_socket)

            if len(local_buffer):
                print("[-->] Received {} bytes form localhost.".format(len(local_buffer)))
                hexdump(local_buffer)

                # send it our request handler
                local_buffer = request_handler(local_buffer)

                # send of data to the remote host
                remote_socket.send(local_buffer)
                print("[-->] send to remote")

                # receive back the response
                remote_buffer = receive_from(remote_socket)

                if len(remote_buffer):
                    print("[<--] Received {} bytes form remote.".format(len(remote_buffer)))
                    hexdump(remote_buffer)

                    # send to our response handler
                    remote_buffer = response_handler(remote_buffer)

                    # send the response to the local socket
                    client_socket.send(remote_buffer)

                    print("[<--] Send to localhost.")

                # if no more data on either side, close the connection
                if not len(local_buffer) or not len(remote_buffer):
                    client_socket.close()
                    remote_socket.close()
                    print("[+] No more data. Closing connection.")
                    break


def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, str) else 2
    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = " ".join(map("{0:0>2X}".format, src))
        text = "".join([chr(x) if 0x20 <= x < 0x7F else "." for x in s])
        result.append("%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text))
    return "\n".join(result)


def receive_from(connection):
    buffer = ""

    # set a 2 second timeout, depending on your target
    connection.settimeout(2)
    try:
        # keep reading into the buffer until there's no more data or time out
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
    return buffer


# modify request destined for the remote host
def request_handler(buffer):
    # perform packet modifications
    return buffer


# modify any responses destined for the local host
def response_handler(buffer):
    # perform packet modification
    return buffer


def main():
    # no fancy command - line parsing
    if len(sys.argv[1:]) != 5:
        print("Usage: ./jtroproxy.py [localhost] [local_port] [remote_host] [remote_port] [receive_first]")
        print("Example: ./jtroproxy.py 127.0.0.1 9595 10.12.132.1 True")
        sys.exit(0)

    # setup local listening parameters
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    # setup remote target
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    # connect and receive data before sending to the remote host
    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    # sign up out listening socket
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


if __name__ == '__main__':
    main()
