#!/usr/bin/env python3
import requests
import csv
import numpy as np
import pandas as pd
import pickle
SIZE_CSV = 15

df = pd.read_csv('dataSet.csv', delimiter=';', encoding='iso-8859-1')
current_df = df[:SIZE_CSV]
with open('new.pickle', 'wb') as f:
	pickle.dump(current_df, f)
files = {'file': ('new.pickle', open('new.pickle', 'rb'))}
r = requests.post("http://localhost:8000", files=files)
our_content = r.content
df = pickle.loads(our_content)
df.to_csv('new_http_answer.csv', encoding='iso-8859-1')
