#!/usr/bin/env python3
import requests
import csv
import numpy as np
import pandas as pd
import pickle
SIZE_CSV = 130

"""Client HTTP"""
df = pd.read_csv('dataSet.csv', delimiter=';', encoding='iso-8859-1')
current_df = df[:SIZE_CSV]
files = {'file': (pickle.dumps(current_df))}
r = requests.post("http://localhost:8000", files=files)
our_content = r.content
df = pickle.loads(our_content)
df.to_csv('new_http_answer.csv', encoding='iso-8859-1')
