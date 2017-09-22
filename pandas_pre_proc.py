# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 11:35:03 2017

@author: vince
"""

import pandas as pd

#to convert unix timestamp to pandas time object
bitcoin = pd.read_csv("btceUSD_1-min_data_2012-01-01_to_2017-05-31.csv")
bitcoin["Timestamp"] = pd.to_datetime(bitcoin.Timestamp, unit='s')
bitcoin.columns = ['Timestamp','Open','High','Low','Close','Volume_BTC','Volume_Currency','Weighted_Price']
bitcoin.set_index('Timestamp', inplace=True)
print(bitcoin.head())

#add a column "Date" / 添加一列日期
bitcoin["Date"] = bitcoin.index.date


bitcoin.Date.value_counts().sort_index().plot()

#resample timestamp of various time range / 重建所需要的时间尺度下得数据
df = pd.DataFrame(columns = ['Open','High','Low','Close','Volume_BTC','Volume_Currency','Weighted_Price'])

#by date
#df["Timestamp"] = bitcoin.groupby(bitcoin.Date).Date.first()
df["Open"] = bitcoin.groupby(bitcoin.Date).Open.first()
df["High"] = bitcoin.groupby(bitcoin.Date).High.max()
df["Low"] = bitcoin.groupby(bitcoin.Date).Low.min()
df["Close"] = bitcoin.groupby(bitcoin.Date).Close.last()
df["Volume_BTC"] = bitcoin.groupby(bitcoin.Date).Volume_BTC.sum()
df["Volume_Currency"] = bitcoin.groupby(bitcoin.Date).Volume_Currency.sum()
df["Weighted_Price"] = df.Volume_Currency / df.Volume_BTC

df.Weighted_Price.plot()

df.to_csv("BTC_date.csv")



#resample by hour / 重建所需要的时间尺度下得数据(hour)
# by hour / 添加一列小时
df_h = pd.DataFrame(columns = ['Open','High','Low','Close','Volume_BTC','Volume_Currency','Weighted_Price'])

#by Date_hour
#df_h["Timestamp"] = ind_h
df_h["Open"] = bitcoin.Open.resample("1H",how = "first")
df_h["High"] = bitcoin.High.resample("1H",how = "max")
df_h["Low"] = bitcoin.Low.resample("1H",how = "min")
df_h["Close"] = bitcoin.Close.resample("1H",how = "last")
df_h["Volume_BTC"] = bitcoin.Volume_BTC.resample("1H",how = "sum")
df_h["Volume_Currency"] = bitcoin.Volume_Currency.resample("1H",how = "sum")
df_h["Weighted_Price"] = df_h.Volume_Currency / df_h.Volume_BTC

df_h.Weighted_Price.plot()
df_h.to_csv("BTC_hour.csv")

















