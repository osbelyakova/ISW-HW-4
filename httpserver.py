#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import io
import numpy as np
import pandas as pd
import pickle
import requests

class RequestHandler(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header("Content-type", "multipart/form-data")
		self.end_headers()
	
	def do_POST(self):
		content_length = int(self.headers['Content-Length'])
		a = self.rfile.read(106)
		our_content = self.rfile.read(content_length - 106)
		df = pickle.loads(our_content)
		s1 = ten_popular_words(df)
		s2 = ten_popular_tweets(df)
		s3 = ten_popular_authors(df)
		s4 = countries_Tweets(df)
		data = pd.concat([s1,s2,s3,s4], axis=1)
		current_df = pickle.dumps(data)
		self._set_headers()
		self.wfile.write(current_df)
		
def ten_popular_words(data):
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
		data = data.loc[:,['Nickname','Followers']]
		data = data.sort_values("Followers", axis=0, ascending=False)
		data = data[:10].reset_index(drop=True)
		data.columns = ['Popular users','Followers']
		return data
		
def ten_popular_tweets(data):
		data = data.loc[:,['RTs','Nickname','Tweet content']]
		data = data.sort_values("RTs", axis=0, ascending=False)
		data = data.loc[:10,['RTs','Nickname','Tweet content']].reset_index(drop=True)
		data.columns = ['RTs','Nickname','Popular tweets']
		return data

def countries_Tweets(data):
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


def run(server_class=HTTPServer, handler_class=RequestHandler, addr="localhost", port=8000):
	server_address = (addr, port)
	httpd = server_class(server_address, handler_class)
	print(f"Starting httpd server on {addr}:{port}")
	httpd.serve_forever()
	
run()