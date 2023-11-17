#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 12:22:48 2023

@author: xingleyang
"""

import numpy as np
import pandas as pd
import datetime as dt
import copy
import statsmodels.api as sm
from stocktrends import Renko
import yfinance as yf

def ATR(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['High']-df['Low'])
    df['H-PC']=abs(df['High']-df['Adj Close'].shift(1))
    df['L-PC']=abs(df['Low']-df['Adj Close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2

def slope(ser,n):
    "function to calculate the slope of n consecutive points on a plot"
    slopes = [i*0 for i in range(n-1)]
    for i in range(n,len(ser)+1):
        y = ser[i-n:i]
        x = np.array(range(n))
        y_scaled = (y - y.min())/(y.max() - y.min())
        x_scaled = (x - x.min())/(x.max() - x.min())
        x_scaled = sm.add_constant(x_scaled)
        model = sm.OLS(y_scaled,x_scaled)
        results = model.fit()
        slopes.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
    return np.array(slope_angle)

def renko_DF(DF):
    "function to convert ohlc data into renko bricks"
    df = DF.copy()
    df.reset_index(inplace=True)
    df = df.iloc[:,[0,1,2,3,4,5]]
    df.columns = ["date","open","high","low","close","volume"]
    df2 = Renko(df)
    df2.brick_size = max(0.5,round(ATR(DF,120)["ATR"][-1],0))
    renko_df = df2.get_ohlc_data()
    renko_df["bar_num"] = np.where(renko_df["uptrend"]==True,1,np.where(renko_df["uptrend"]==False,-1,0))
    for i in range(1,len(renko_df["bar_num"])):
        if renko_df["bar_num"][i]>0 and renko_df["bar_num"][i-1]>0:
            renko_df["bar_num"][i]+=renko_df["bar_num"][i-1]
        elif renko_df["bar_num"][i]<0 and renko_df["bar_num"][i-1]<0:
            renko_df["bar_num"][i]+=renko_df["bar_num"][i-1]
    renko_df.drop_duplicates(subset="date",keep="last",inplace=True)
    return renko_df

def OBV(DF):
    """function to calculate On Balance Volume"""
    df = DF.copy()
    df['daily_ret'] = df['Adj Close'].pct_change()
    df['direction'] = np.where(df['daily_ret']>=0,1,-1)
    df['direction'][0] = 0
    df['vol_adj'] = df['Volume'] * df['direction']
    df['obv'] = df['vol_adj'].cumsum()
    return df['obv']

def CAGR(DF):
    "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
    df = DF.copy()
    df["cum_return"] = (1 + df["ret"]).cumprod()
    n = len(df)/(252*78)
    CAGR = (df["cum_return"].tolist()[-1])**(1/n) - 1
    return CAGR

def volatility(DF):
    "function to calculate annualized volatility of a trading strategy"
    df = DF.copy()
    vol = df["ret"].std() * np.sqrt(252*78)
    return vol

def sharpe(DF,rf):
    "function to calculate sharpe ratio ; rf is the risk free rate"
    df = DF.copy()
    sr = (CAGR(df) - rf)/volatility(df)
    return sr
    

def max_dd(DF):
    "function to calculate max drawdown"
    df = DF.copy()
    df["cum_return"] = (1 + df["ret"]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd


# Download historical data for DJI constituent stocks

tickers = ["MSFT","AAPL","AMZN","INTC", "CSCO","VZ","IBM","QCOM","LYFT"]
ticker = "MSFT"

ohlc_intraday = {} # directory with ohlc value for each stock            

for ticker in tickers:
    ohlc_intraday[ticker] = yf.download(ticker, period = "1mo", interval = "5m")
    ohlc_intraday[ticker].dropna(how = "all", inplace = True)
    
################################Backtesting####################################

#Merging renko df with original ohlc df
ohlc_df = copy.deepcopy(ohlc_intraday)
ohlc_renko = {}

signal = {}
return_value = {}

for ticker in tickers:
    renko = renko_DF(ohlc_df[ticker])
    ohlc_df[ticker]["date"] = ohlc_df[ticker].index
    ohlc_renko[ticker] = ohlc_df[ticker].merge(renko.loc[:,["date","bar_num"]],how = "outer", on = "date")
    ohlc_renko[ticker]["bar_num"].fillna(method = "ffill", inplace = True)
    ohlc_renko[ticker]["obv"] = OBV(ohlc_df[ticker])
    ohlc_renko[ticker]["obv_degree"] = slope(ohlc_renko[ticker]["obv"], 5)
    signal[ticker] = ""
    return_value[ticker]= []
    
    
#Identifying signals and calculating daily return
for ticker in tickers:
    for i in range(1, len(ohlc_df)):
        if signal[ticker] == "":
            return_value[ticker].append(0)
            
            if ohlc_renko[ticker]["bar_num"][i] > 2 and ohlc_renko[ticker]["obv_degree"][i] > 30:
                signal[ticker] = "Buy"
            elif ohlc_renko[ticker]["bar_num"][i] <= -2 and ohlc_renko[ticker]["obv_degree"][i] < -30:
                signal[ticker] = "Sell"
                
        elif signal[ticker] == "Buy":
             return_value[ticker].append((ohlc_renko[ticker]["Adj Close"][i]/ohlc_renko[ticker]["Adj Close"][i-1])-1)
             
             if ohlc_renko[ticker]["bar_num"][i] < 2 :
                 signal[ticker] = ""
             elif ohlc_renko[ticker]["bar_num"][i] <= -2 and ohlc_renko[ticker]["obv_degree"][i] < -30:
                 signal[ticker] = "Sell"
                 
        elif signal[ticker] == "Sell":
             return_value[ticker].append((ohlc_renko[ticker]["Adj Close"][i-1]/ohlc_renko[ticker]["Adj Close"][i])-1)
             if ohlc_renko[ticker]["bar_num"][i] > -2 :
                 signal[ticker] = ""
             elif   ohlc_renko[ticker]["bar_num"][i] > 2 and ohlc_renko[ticker]["obv_degree"][i] > 30:
                  signal[ticker] = "Buy"

    ohlc_renko[ticker]["ret"] = np.array(return_value[ticker])

strategy_df = pd.DataFrame()
for ticker in tickers:
    strategy_df[ticker] = ohlc_renko[ticker]["ret"]
    
strategy_df["ret"] = strategy_df.mean(axis = 1)

#KPI
CAGR(strategy_df)
sharpe(strategy_df,0.025)
max_dd(strategy_df)  

#visualizing strategy returns
(1+strategy_df["ret"]).cumprod().plot()

#calculating individual stock's KPIs
cagr = {}
sharpe_ratios = {}
max_drawdown = {}

for ticker in tickers:
    cagr[ticker] = CAGR(ohlc_renko[ticker])
    sharpe_ratios[ticker] = sharpe(ohlc_renko[ticker], 0.025)
    max_drawdown[ticker] =  max_dd(ohlc_renko[ticker])









