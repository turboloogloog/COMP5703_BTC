import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib import style
import numpy as np
import pandas as pd
import datetime as dt
from scipy.signal import argrelextrema
from scipy.spatial.distance import  euclidean
import urllib.request


style.use("default")

THRESHOLD_1 = 60
THRESHOLD_2 = 50

MA1 = 10
MA2 = 30

INIT = 1000
TRADING_SCALE = 0.25

def moving_average(values, window):
    weights = np.repeat(1.0, window)/window
    smas = np.convolve(values, weights, 'valid')
    return smas

def shiftEcu(key_points, shift_length = 1):
    shift_variance = []
    for i,j in zip(key_points, key_points[shift_length:]):
        shift_variance.append((j[0],euclidean(i,j)))
    return shift_variance

def thresholding(shift_variance, THRESHOLD):
    turning_index = [x for x,y in shift_variance if y >= THRESHOLD]
    turning_point = [x for x in key_points if x[0] in turning_index]
    return turning_index, turning_point

def graph_data():
    ax1 = plt.subplot2grid((6,1), (1,0), colspan=1, rowspan=4)
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.ylabel('Price')
    
    ax2 = plt.subplot2grid((6,1), (0,0), colspan=1, rowspan=1, sharex=ax1)
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.title('BTC visualization, smoothed with alpha = 0.1') 
    plt.ylabel("MAvgs")
    ax2v = ax2.twinx()
    
    ax3 = plt.subplot2grid((6,1), (5,0), colspan=1, rowspan=1, sharex=ax1)
    plt.ylabel("Profit")
    plt.xlabel('Year')
    ax3v = ax3.twinx()
    # =============================================================================
    #     configure of ax1 -- Price & smoothing 
    # =============================================================================
    ax1.grid(True)
    
    bbox_props = dict(boxstyle='round4',fc='w', ec='k',lw=1)
    ax1.annotate(str(price[price.index[-1]]), (x[-1], price[price.index[-1]]), 
                 xytext = (x[-1]+dt.timedelta(days=10), price[price.index[-1]]),bbox=bbox_props)
    
    ax1.plot(x[-start:],price[-start:], label='Observed',zorder=1)
    ax1.plot(x[-start:],data[-start:], '-r', label='Smoothed',zorder=1)
    ax1.scatter(x[turning_max["x"]], price[turning_max["x"]], label="Max turning point", marker='o', color='r', zorder=2)
    ax1.scatter(x[turning_min["x"]], price[turning_min["x"]], label="Min turning point", marker='o', color='g', zorder=2)
    ax1.legend(loc=0)
    
    # =============================================================================
    #     configure of ax2 -- Moving average & Volume
    # =============================================================================
    ax2.grid(True)
    ax2.plot(x[-start:], ma1[-start:], label = "Window = 10")
    ax2.plot(x[-start:], ma2[-start:],"-", label = "Window = 30")
    ax2.fill_between(x[-start:], ma2[-start:], ma1[-start:], where=(ma1[-start:] < ma2[-start:]), facecolor='r', edgecolor='r', alpha=0.5)
    ax2.fill_between(x[-start:], ma2[-start:], ma1[-start:], where=(ma1[-start:] > ma2[-start:]), facecolor='g', edgecolor='g', alpha=0.5)
  
    ax2v.plot(x[-start:], volume[-start:], label='volume')
    ax2.legend(loc=0)
    
    # =============================================================================
    #     configure of ax3 -- Turning points & Profit
    # =============================================================================
    for label in ax3.xaxis.get_ticklabels():
        label.set_rotation(45)
    ax3.grid(True)
    ax3.plot(x[turning_max["x"]], list(turning_max["y"]), label="Max turning point", marker='o', color='r', zorder=2)
    ax3.plot(x[turning_min["x"]], list(turning_min["y"]), label="Min turning point", marker='o', color='g', zorder=2)
    ax3.plot(x[turning_point["x"]], list(turning_point["y"]), label="Turning point", marker='o', color='k', zorder=1)
    
    buf = get_profit(turning_max, turning_min, turning_point, INIT, TRADING_SCALE)
    
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax3.xaxis.set_major_locator(mticker.MaxNLocator(10))
    ax3v.bar(x[buf['x']], buf['total'].values, width = 5)
    ax3.legend(loc=0)
    
def get_data():
    with urllib.request.urlopen('https://data.bitcoinity.org/export_data.csv?currency=USD&data_type=price_volume&r=day&t=lb&timespan=all&vu=curr') as response:
       html = response.read()
       
    file_list = html.decode().split('\n')
    BTC = {'Time': [], 'price': [], 'volume': []}
    
    for line in file_list[1:]:
        if not line:
            pass
        else:
            Time, price, volume = line.split(",")
            BTC["Time"].append(Time)
            BTC["price"].append(price)
            BTC["volume"].append(volume)
    
    return pd.DataFrame.from_dict(BTC)    

def get_profit(turning_max, turning_min, turning_point, INIT, TRADING_SCALE):        
    currency = INIT
    BTC = 0
    buf = {"BTC" : [], "currency" : []}
    for i in range(len(turning_point)):
        if turning_point['x'].iloc[i] in max_index:
            if BTC > 0:
                BTC = BTC - BTC*TRADING_SCALE
                currency = currency + turning_point['y'].iloc[i].astype(float) * (BTC*TRADING_SCALE)
                buf.get('BTC').append((turning_point['x'].iloc[i], BTC))
                buf.get('currency').append((turning_point['x'].iloc[i], currency))
        else:
            if currency > 0:
                BTC = BTC + (currency*TRADING_SCALE) / turning_point['y'].iloc[i].astype(float)
                currency = currency - currency*TRADING_SCALE
                buf.get('BTC').append((turning_point['x'].iloc[i], BTC))
                buf.get('currency').append((turning_point['x'].iloc[i], currency))
    
    BTC = pd.DataFrame(buf['BTC'], columns = ["x","BTC_Vol"])
    currency = pd.DataFrame(buf['currency'], columns = ["x","Cur_Vol"])
    buf = BTC.merge(currency, left_on='x', right_on='x', how = 'inner')
    
    buf['total'] = pd.np.multiply(buf['BTC_Vol'], price[buf['x']]) + buf['Cur_Vol']
            
    return buf


if __name__ == "__main__":        
    # =============================================================================
    # loading data
    # =============================================================================
    #SP = pd.read_csv('bitcoinity_data.csv') #from local file
    SP = get_data()                         #from web


    #assign data
    dates = SP[SP.columns[0]] 
    price = SP[SP.columns[1]].astype(float)
    volume = SP[SP.columns[2]].astype(float)
    
    ma1 = moving_average(price,MA1)
    ma2 = moving_average(price,MA2)
    start = len(dates[MA2-1:])
    
    x = np.array([dt.datetime.strptime(d, '%Y-%m-%d %H:%M:%S UTC') for d in dates]) #data stamp
    data = price.ewm(alpha = 0.3).mean() #smoothed price
    data = data[:round(len(data)/1)]
    data = np.array(data)
    
    # =============================================================================
    #Finding potential turning point
    # =============================================================================
    # local maxima
    index_max = argrelextrema(data, np.greater)
    index_max = np.array(index_max[0])
    
    # local minima
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
    turning_max = pd.DataFrame(turning_max, columns = ["x","y"])
    turning_min = pd.DataFrame(turning_min, columns = ["x","y"])
    turning_point = turning_max.append(turning_min, ignore_index=True)
    turning_point = turning_point.sort_values("x", axis=0)
    turning_point['y'] = list(price[sorted(max_index+min_index)])
    
    
    GRAPH_INDEX = len(x)
    x = x[:GRAPH_INDEX]
    price = price[:GRAPH_INDEX]
    
    # =============================================================================
    # comment this next line to plotting all data
    # =============================================================================
    start = len(x) - turning_point["x"][0]
    
    graph_data()


