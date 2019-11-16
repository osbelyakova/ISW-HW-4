#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import io
import numpy as np
import pandas as pd
import pickle
import requests
import multiprocessing
from pycorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('http://localhost:9000')

"""Server HTTP"""
class RequestHandler1(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header("Content-type", "multipart/form-data")
		self.end_headers()
	
	def do_POST(self):
		content_length = int(self.headers['Content-Length'])
		a = self.rfile.read(100)
		our_content = self.rfile.read(content_length - 100)
		df = pickle.loads(our_content)
		s1 = ten_popular_words(df)
		s2 = ten_popular_tweets(df)
		s3 = ten_popular_authors(df)
		s4 = countries_Tweets(df)
		s1[' '] = ""
		s4[' '] = ""
		s3[' '] = ""
		data = pd.concat([s1,s4,s3,s2], axis=1)
		current_df = pickle.dumps(data)
		self._set_headers()
		self.wfile.write(current_df)

class RequestHandler2(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header("Content-type", "multipart/form-data")
		self.end_headers()
			
	def do_POST(self):
		content_length = int(self.headers['Content-Length'])
		a = self.rfile.read(100)
		our_content = self.rfile.read(content_length - 100)
		data = pickle.loads(our_content)
		data = data.loc[:,['Tweet content']]
		l = []
		m = []
		for i in data.index:
			text = data.iloc[i]['Tweet content']
			result = nlp.annotate(text, properties={'annotators': 'ner','outputFormat': 'json','timeout': 100000,})
			pos = []
			for word in result["sentences"][0]["tokens"]:
				pos.append('{} ({})'.format(word["word"], word["ner"]))
			m.append(" ".join(pos))
			l.append(m)
			m = []
		data = pd.DataFrame(l)
		current_df = pickle.dumps(data)
		self._set_headers()
		self.wfile.write(current_df)
		
		
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
	data2 = data.loc[l2,['Country']]
	data1 = data1.drop_duplicates(subset=['Country'], keep="last")
	data2 = data2.drop_duplicates(subset=['Country'], keep="last")
	data1 = data1.sort_values("Country", axis=0, ascending=False).reset_index(drop=True)
	data2 = data2.sort_values("Country", axis=0, ascending=False).reset_index(drop=True)
	data = pd.concat([data1,data2], axis=1)
	data.columns = ['Country with Tweets','Country with RTs']
	return data


def run_stat(server_class=HTTPServer, handler_class=RequestHandler1, addr="localhost", port=8000):
	server_address = (addr, port)
	httpd = server_class(server_address, handler_class)
	print(f"Starting stat httpd server on {addr}:{port}")
	httpd.serve_forever()
	
def run_enti(server_class=HTTPServer, handler_class=RequestHandler2, addr="localhost", port=8001):
	server_address = (addr, port)
	httpd = server_class(server_address, handler_class)
	print(f"Starting enti httpd server on {addr}:{port}")
	httpd.serve_forever()

stat = multiprocessing.Process(target=run_stat, args=())
enti = multiprocessing.Process(target=run_enti, args=())
stat.start()
enti.start()
stat.join()
enti.join()
