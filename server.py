#!/usr/bin/env python3
import socket
import threading
import multiprocessing
import os
import csv
import numpy as np
import pandas as pd
import pickle
import sys
from pycorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('http://localhost:9000')

"""Server"""
def process_request(conn, addr):
	"""Choose the command to execute"""
	print("connected client:", addr)
	with conn:
		while True:
			data = conn.recv(1024)
			if not data:
				break
			conn.send("OK".encode("utf-8"))
			first_message = data.decode("utf-8")
			size = int(first_message[7:-1])
			data2 = conn.recv(size)
			df = pickle.loads(data2)
			if (first_message[1:5] == "STAT"):
				do_STAT(df, conn, addr)
			if (first_message[1:5] == "ENTI"):
				do_ENTI(df, conn, addr)
		conn.close()

def do_STAT(df, conn, addr):
	"""if STAT"""
	s1 = ten_popular_words(df)
	s2 = ten_popular_tweets(df)
	s3 = ten_popular_authors(df)
	s4 = countries_Tweets(df)
	s1['   '] = ""
	s2['   '] = ""
	s3['   '] = ""
	data = pd.concat([s1,s2,s3,s4], axis=1)
	current_df = pickle.dumps(data)
	byte_size = str(sys.getsizeof(current_df))
	conn.send(byte_size.encode("utf-8"))
	answer = conn.recv(50)
	conn.send(current_df)
	return 0
	
def ten_popular_words(data):
	"""Looking for 10 popular words in data"""
	data = data.loc[:,['Tweet content']]
	l = []
	col = []
	d = {}
	for i in data.index:
		text = data.iloc[i]['Tweet content']
		for word in text.split():
			if (word != "RT"):
				d[word] = d.get(word,0) + 1
	for i in range(0,10):
		pop_word = max(d, key=d.get)
		del d[pop_word]
		l.append(pop_word)
		col.append(l)
		l = []
	data = pd.DataFrame(col,columns=['Popular words'])
	return data
			
def ten_popular_authors(data):
	"""Looking for 10 popular authors in data"""
	data = data.loc[:,['Nickname','Followers']]
	data = data.sort_values("Followers", axis=0, ascending=False)
	data = data[:10].reset_index(drop=True)
	data['Followers'].replace('',np.nan, inplace=True)
	data.dropna(subset=['Followers'], inplace=True)
	data.columns = ['Popular users','Followers']
	return data
	
def ten_popular_tweets(data):
	"""Looking for 10 popular tweets in data"""
	data = data.loc[:,['RTs','Nickname','Tweet content']]
	data = data.sort_values("RTs", axis=0, ascending=False)
	data = data.drop_duplicates(subset=['Tweet content'], keep="last")
	data = data[:10].reset_index(drop=True)
	data['RTs'].replace('',np.nan, inplace=True)
	data.dropna(subset=['RTs'], inplace=True)
	data.columns = ['RTs','Nickname','Popular tweets']
	return data

def countries_Tweets(data):
	"""Looking for countries with Tweets and RTweets"""
	l1 = []
	l2 = []
	for i in data.index:
		if (data.iloc[i]['Tweet content'].find("RT") == -1):
			l1.append(i)
		else:
			l2.append(i)
	data1 = data.loc[l1,['Country']]
	data1 = data1.sort_values("Country", axis=0, ascending=False).reset_index(drop=True)
	data2 = data.loc[l2,['Country']]
	data2 = data2.sort_values("Country", axis=0, ascending=False).reset_index(drop=True)
	data = pd.concat([data1,data2], axis=1)
	data.columns = ['Country with Tweets','Country with RTs']
	return data

def do_ENTI(data, conn, addr):
	"""if ENTI"""
	data = data.loc[:,['Tweet content']]
	l = []
	for i in data.index:
		text = data.iloc[i]['Tweet content']
		result = nlp.annotate(text, properties={'annotators': 'ner','outputFormat': 'json','timeout': 100000,})
		pos = []
		for word in result["sentences"][0]["tokens"]:
			pos.append('{} ({})'.format(word["word"], word["ner"]))
		" ".join(pos)	
		l.append(pos)
	data = pd.DataFrame(l)
	current_df = pickle.dumps(data)
	byte_size = str(sys.getsizeof(current_df))
	conn.send(byte_size.encode("utf-8"))
	answer = conn.recv(50)
	conn.send(current_df)
	return 0

def worker(sock):
	"""Processes"""
	while True:
		conn, addr = sock.accept()
		print("pid", os.getpid())
		th = threading.Thread(target=process_request, args=(conn, addr))
		th.start()

with socket.socket() as sock:
	sock.bind(("", 3000))
	sock.listen()
	workers_count = 3
	workers_list = [multiprocessing.Process(target=worker, args=(sock,))
					for _ in range(workers_count)]
	
	for w in workers_list:
		w.start()
	
	for w in workers_list:
		w.join()
