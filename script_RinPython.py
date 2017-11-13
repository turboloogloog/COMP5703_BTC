# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 15:29:54 2017

@author: vince
"""
#from turningPoint_ewm_smooth import get_data
#from collections import defaultdict
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from turningPoint_ewm_smooth import get_data


def call_RMC():
    proc = subprocess.Popen(['C:\\Program Files\\R\\R-3.4.1\\bin\\x64\\RScript','C:\\Users\\vince\\Desktop\\5703_playground\\markov_chain_BTC.R'], 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()

#call_RMC()

features = pd.read_csv("zigzag_features.csv")
features = features["Event_Pattern"]
features = set(features)


unique_p = []
for feature in features:
    temp = []
    temp = feature.split(',')
    unique_p += temp
    
unique_p = set(unique_p)
unique_p_no = list(range(len(unique_p)))
unique_p = dict(zip(unique_p, unique_p_no))

f = []
for feature in features:
    temp = feature.split(',')
    f.append([unique_p[x] for x in temp])
    
newdict = {}
for key, value in unique_p.items():
    newdict.setdefault(value, []).append(key)
    
pred_index = pd.read_csv('zigzag_predicted.csv')
pred_index = list(pred_index['x'])
last_price = float(price[[price.index[-10]]])
last_price_gap = abs(last_price -  float(price[[price.index[-2]]]))

pred_price = [last_price_gap*i + last_price for i in pred_index]

ax = plt.subplot()
plt.ylabel('Price')
plt.plot(price)
