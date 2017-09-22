#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
from scipy.signal import argrelextrema
from scipy.spatial.distance import  euclidean
#from scipy.ndimage.interpolation import shift
#from scipy.spatial.distance import  euclidean

THRESHOLD_1 = 60
THRESHOLD_2 = 50

def shiftEcu(key_points, shift_length = 1):
    shift_variance = []
    for i,j in zip(key_points, key_points[shift_length:]):
        shift_variance.append((j[0],euclidean(i,j)))
    return shift_variance

def thresholding(shift_variance, THRESHOLD):
    turning_index = [x for x,y in shift_variance if y >= THRESHOLD]
    turning_point = [x for x in key_points if x[0] in turning_index]
    return turning_index, turning_point
  
SP = pd.read_csv('BTC_date.csv')
closePrice = SP[SP.columns[4]] 
dates = SP[SP.columns[0]] 
x = np.array([dt.datetime.strptime(d, '%Y-%m-%d') for d in dates])
data = closePrice.ewm(alpha = 0.2).mean()
data = data[:round(len(data)/1)]
data = np.array(data)

# for local maxima
index_max = argrelextrema(data, np.greater)
index_max = np.array(index_max[0])

# for local minima
index_min = argrelextrema(data, np.less)
index_min = np.array(index_min[0])

max_set = np.take(data, index_max)
min_set = np.take(data, index_min)
        
Max = [l for l in zip(index_max, max_set)]
Min = [l for l in zip(index_min, min_set)]

key_points = Max + Min 
#sort by index
key_points = sorted(key_points, key = lambda x: x[0])


#calcualte euclidean distance
shift_variance =  shiftEcu(key_points)
#adding thresold, filter dramatic change
turning_index, turning_point = thresholding(shift_variance, THRESHOLD_1)



#reasign turning point to local max and local min set
turning_max = [x for x in turning_point if x in Max]
turning_min = [x for x in turning_point if x in Min]

#calculate euclidean distance for adjcant local extreme point
shifted_max = shiftEcu(turning_max)
shifted_min = shiftEcu(turning_min)

#for adjcant max or min point, apply a second threshold
max_index, turning_max = thresholding(shifted_max, THRESHOLD_2)
min_index, turning_min = thresholding(shifted_min, THRESHOLD_2)

        
fig2 = plt.figure()
plt.plot(closePrice, label='Observed')
plt.plot(data, '-r', label='Smoothed')
plt.plot(*zip(*turning_max), marker='o', color='r', ls='')
plt.plot(*zip(*turning_min), marker='o', color='g', ls='')
plt.title('BTC Close Price, smoothed with alpha = 0.1') 
plt.xlabel('Year')
plt.ylabel('Close Price')
plt.legend(loc=1)  













