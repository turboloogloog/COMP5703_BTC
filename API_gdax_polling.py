# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 16:14:03 2017

@author: vince
"""

import gdax
import dateutil.parser

#initial a public client instance
public_client = gdax.PublicClient()

#get useful information 
now           = public_client.get_time()
BTC_trades    = public_client.get_product_trades(product_id='BTC-USD')
order_book_2  = public_client.get_product_order_book('BTC-USD', level=2)
BTC_24h_stats = public_client.get_product_24hr_stats('BTC-USD')

#convert time stamp from string to datetime object
dateutil.parser.parse(now["iso"])

wsClient = gdax.WebsocketClient(url="wss://ws-feed.gdax.com", products="BTC-USD")