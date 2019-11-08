#!/usr/bin/env python3
import socket
import csv

message = input()
with socket.create_connection(("127.0.0.1", 3001)) as sock:
    sock.sendall(message.encode("utf8"))
    sock.sendall()
    while True:
		answer = sock.recv(1024)
		if not answer:
			break
