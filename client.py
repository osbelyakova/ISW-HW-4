#!/usr/bin/env python3
import socket
import csv
import sys
import numpy as np
import pandas as pd
import pickle
		
message = "[ENTI][3]"
size = int(message[7:-1])
df = pd.read_csv('dataSet.csv', delimiter=';', encoding='iso-8859-1')
current_df = pickle.dumps(df[:size+1])
byte_size = str(sys.getsizeof(current_df))
message = message[:7] + byte_size + ']'
with socket.create_connection(("127.0.0.1", 3000)) as sock:
	sock.send(message.encode("utf-8"))
	answer = sock.recv(50)		
	sock.sendall(current_df)
	answer = sock.recv(50)
	size = int(answer.decode('utf-8'))
	sock.send("OK".encode("utf-8"))
	df = sock.recv(size)
	data = pickle.loads(df)
	data.to_csv('new_tcp_answer.csv', encoding='iso-8859-1')
