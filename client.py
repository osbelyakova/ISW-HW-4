#!/usr/bin/env python3
import socket
import csv
import sys
		
def make_csv(data):
	s = data.decode("utf-8")
	l = []
	while s.find(']') > 0:
		i = s.find(']')
		substr = s[2:i - 1]
		m = []
		while substr.find(';') > 0:
			j = substr.find(';') + 1
			m.append(substr[:j - 1])
			substr = substr[j:]
		m.append(substr)
		l.append(m)
		s = s[i + 1:]
		
message = input()
with socket.create_connection(("127.0.0.1", 3020)) as sock:
	NUMBER_OF_LINES = int(message[7:-1])
	s = ""
	with open('dataSet.csv', newline="", encoding="ISO-8859-1") as csv_file:
		reader = csv.reader(csv_file)
		for i in range(0,NUMBER_OF_LINES+1):
			l = str(next(reader))
			s = s + l
		LENGHT_IN_BYTES = sys.getsizeof(s)
		message = message[:7] + str(LENGHT_IN_BYTES) +']'
		sock.sendall(message.encode("utf-8"))
		sock.sendall(s.encode("utf-8"))
		#while True:
			#answer = sock.recv(1024)
			#if not answer:
				#break
