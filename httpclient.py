#!/usr/bin/env python3
import requests
import csv
import numpy as np
import pandas as pd
import pickle

"""Client HTTP"""
message = input("Enter your request: ")
SIZE_CSV = int(message[7:-1])
df = pd.read_csv('dataSet.csv', delimiter=';', encoding='iso-8859-1')
current_df = df[:SIZE_CSV]
files = {'file': (pickle.dumps(current_df))}
if (message[1:5] == "STAT"):
	r = requests.post("http://localhost:8000", files=files)
elif (message[1:5] == "ENTI"):
	r = requests.post("http://localhost:8001", files=files)
else:
	print("ERROR")
our_content = r.content
df = pickle.loads(our_content)
if (message[1:5] == "STAT"):
	df.to_csv('data_http_answer.csv', encoding='iso-8859-1')
elif (message[1:5] == "ENTI"):
	df.to_csv('entities_http_answer.csv', encoding='iso-8859-1')
