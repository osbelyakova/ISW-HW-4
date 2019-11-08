#!/usr/bin/env python3
import socket
import threading
import multiprocessing
import os
import csv
#from pycorenlp import StanfordCoreNLPnlp = StanfordCoreNLP('http://localhost:9000')

def process_request(conn, addr):
	print("connected client:", addr)
	with conn:
		while True:
			data = conn.recv(1024)
			if not data:
				break
			first_message = data.decode("utf-8")
			size = first_message[7:-1]
			if (first_message[1:5] == "STAT"):
				do_STAT(int(size), conn, addr)
			if (first_message[1:5] == "ENTI"):
				do_ENTI(int(size), conn, addr)
		conn.close()

def do_STAT(csv_size, conn, addr):
	print("make STAT for:", addr)
	with conn:
		while True:
			data = conn.recv(csv_size)
			if not data:
				break
			FILE_NAME = make_csv(data)
			s = ten_popular_words(FILE_NAME)
			#отправку клиенту реализовать

def ten_popular_words(file_name):
	with open(file_name, newline="", encoding="ISO-8859-1") as csv_file:
		reader = csv.reader(csv_file)
		s = ""
		flag = 1
		for row in reader:
			if flag:
				flag = 0
				continue
			if row[6] != "":
				s = s + str(row[6])+ ' '
		csv_file.close()
	l = []
	s.lstrip()
	substr = ""
	for a in s:
		if a == ' ':
			substr.lstrip()
			l.append(substr)
			s.lstrip()
			substr = ""
		else:
			substr = substr + a
	l.sort()
	l_10 = []
	k_10 = []
	l.remove('')
	while l != []:
		word = l[0]
		k = l.count(word)
		if len(l_10) < 10:
			l_10.append(word)
			k_10.append(k)
		else:
			if min(k_10) < k:
				for i in k_10:
					if k_10[i] == min(k_10):
						l_10[i] = word
						k_10[i] = k
						break
		for i in range(0, k):
			l.remove(word)
	return l_10
			
					
			
def make_csv(data):
	s = data.decode("utf-8")
	l = []
	i = s.find(']')
	while i > 0:
		substr = s[2:i - 1]
		m = []
		j = substr.find(';') + 1
		while j > 0:
			m.append(substr[:j - 1])
			substr = substr[j:]
			j = substr.find(';') + 1
		m.append(substr)
		l.append(m)
		s = s[i + 1:]
		i = s.find(']')
	with open("server_csv.csv", "w", newline="") as f:
		writer = csv.writer(f)
		writer.writerows(l)
		f.close()
	return "server_csv.csv"

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
	return 0

def worker(sock):
	while True:
		conn, addr = sock.accept()
		print("pid", os.getpid())
		th = threading.Thread(target=process_request, args=(conn, addr))
		th.start()

with socket.socket() as sock:
	sock.bind(("", 3020))
	sock.listen()
	workers_count = 3
	workers_list = [multiprocessing.Process(target=worker, args=(sock,))
					for _ in range(workers_count)]
	
	for w in workers_list:
		w.start()
	
	for w in workers_list:
		w.join()
