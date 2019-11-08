#!/usr/bin/env python3
import socket
import threading
import multiprocessing
import os
import csv
from pycorenlp import StanfordCoreNLPnlp = StanfordCoreNLP('http://localhost:9000')

def process_request(conn, addr):
    print("connected client:", addr)
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            first_message = data.decode("utf8")
            size = first_message[7:-1]
            if (first_message[1:5] == STAT):
                do_STAT(size, conn, addr)
            if (first_message[1:5] == ENTI):
                do_ENTI(size, conn, addr)

def do_STAT(csv_size, conn, addr):
    print("make STAT for:", addr)
    with conn:
        while True:
            data = conn.recv(csv_size)
            if not data:
                break
            make_stat_analysis(data)
			#отправку клиенту реализовать
			
def make_stat_analysis(data):
	

def do_ENTI(csv_size, conn, addr):
    print("make ENTI for:", addr)
    with conn:
        while True:
            data = conn.recv(csv_size)
            if not data:
                break
            take_entities(data)
			#отправку клиенту реализовать
			
def take_entities(data):
	

def worker(sock):
    while True:
        conn, addr = sock.accept()
        print("pid", os.getpid())
        th = threading.Thread(target=process_request, args=(conn, addr))
        th.start()

with socket.socket() as sock:
    sock.bind(("", 3001))
    sock.listen()
    
    workers_count = 3
    workers_list = [multiprocessing.Process(target=worker, args=(sock,))
                    for _ in range(workers_count)]
    
    for w in workers_list:
        w.start()
    
    for w in workers_list:
        w.join()
