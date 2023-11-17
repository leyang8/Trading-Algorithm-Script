#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 15 13:20:04 2023

@author: xingleyang
"""

import numpy as np
import pandas as pd
import yfinance as yf
import copy
import datetime as dt

#define all technical index will be used

def CAGR(DF):
    "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
    df = DF.copy()
    df["cum_return"] = (1 + df["ret"]).cumprod()
    n = len(df)/(252*7)
    CAGR = (df["cum_return"].tolist()[-1])**(1/n) - 1
    return CAGR
    "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
    df = DF.copy()
    df["cum_return"] = (1 + df["ret"]).cumprod()
    n = len(df)/(252*78)
    CAGR = (df["cum_return"].tolist()[-1])**(1/n) - 1
    return CAGR

def volatility(DF):
    "function to calculate annualized volatility of a trading strategy"
    df = DF.copy()
    vol = df["ret"].std() * np.sqrt(252*7)
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

def ATR(DF,n=20):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['High']-df['Low'])
    df['H-PC']=abs(df['High']-df['Adj Close'].shift(1))
    df['L-PC']=abs(df['Low']-df['Adj Close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2['ATR']

# Download historical data (monthly) for selected stocks
tickers = ["MSFT","AAPL","AMZN","INTC", "CSCO","VZ","IBM","TSLA","AMD"]

ohlcv_data = {}

for ticker in tickers:
    ohlcv_data[ticker] = yf.download(ticker, interval = "1h", period = "3mo")
    ohlcv_data[ticker].drop("Close", axis = 1, inplace  = True)
    ohlcv_data[ticker].dropna(inplace = True, how = "any")
    

################################Backtesting####################################

# calculating ATR and rolling max price for each stock and consolidating this info by stock in a separate dataframe
ohlcv_dict = copy.deepcopy(ohlcv_data)

# setting two data structure, one storing trading status and the other storing return values
signal = {}
return_value = {}

for ticker in tickers:
    ohlcv_dict[ticker]["ATR"] = ATR(ohlcv_dict[ticker])
    ohlcv_dict[ticker]["rolling_high_max"] = ohlcv_dict[ticker]["High"].rolling(20).max()
    ohlcv_dict[ticker]["rolling_low_min"] = ohlcv_dict[ticker]["Low"].rolling(20).min()
    ohlcv_dict[ticker]["rolling_max_vol"] = ohlcv_dict[ticker]["Volume"].rolling(20).max()
    ohlcv_dict[ticker].dropna(inplace = True)
    #initial signal as "", return as 0
    signal[ticker] = ""
    return_value[ticker] = [0]
    
#based on different signal, operate differently
for ticker in tickers: #iterating each tickers
    for i in range(1,len(ohlcv_dict[ticker])):  #iterating each hour
        if signal[ticker] == "":
            return_value[ticker].append(0)
            
            if ohlcv_dict[ticker]["High"][i] >= ohlcv_dict[ticker]["rolling_high_max"][i] and \
               ohlcv_dict[ticker]["Volume"][i] > 1.5 * ohlcv_dict[ticker]["rolling_max_vol"][i-1]:
                   signal[ticker] = "buy"
                   
           
            elif ohlcv_dict[ticker]["Low"][i] <= ohlcv_dict[ticker]["rolling_low_min"][i] and \
               ohlcv_dict[ticker]["Volume"][i] > 1.5 * ohlcv_dict[ticker]["rolling_max_vol"][i-1]:
                   signal[ticker] = "sell"
                
              
        elif signal[ticker] == "buy":
            # the stop loss point is met(sell out)
            if ohlcv_dict[ticker]["Low"][i] < ohlcv_dict[ticker]["Adj Close"][i-1] - ohlcv_dict[ticker]["ATR"][i-1]:
                signal[ticker] = ""
                #computing the current candle return
                return_value[ticker].append(((ohlcv_dict[ticker]["Adj Close"][i-1] - ohlcv_dict[ticker]["ATR"][i-1]) / ohlcv_dict[ticker]["Adj Close"][i-1]) - 1)
             
            #the sell signal is met(price drop down all of a sudden)
            elif ohlcv_dict[ticker]["Low"][i] <= ohlcv_dict[ticker]["rolling_low_min"][i] and \
               ohlcv_dict[ticker]["Volume"][i] > 1.5 * ohlcv_dict[ticker]["rolling_max_vol"][i-1]:
                   signal[ticker] = "sell"
        
                   return_value[ticker].append((ohlcv_dict[ticker]["rolling_low_min"][i] / ohlcv_dict[ticker]["Adj Close"][i-1] )- 1)
                
            else:
                return_value[ticker].append((ohlcv_dict[ticker]["Adj Close"][i] / ohlcv_dict[ticker]["Adj Close"][i-1]) - 1)
         
        elif signal[ticker] == "sell":
            # the selling signal is end
            if ohlcv_dict[ticker]["High"][i] > ohlcv_dict[ticker]["Adj Close"][i-1] + ohlcv_dict[ticker]["ATR"][i-1]:
                signal[ticker] = ""
  
                #computing the current candle return
            
                return_value[ticker].append((ohlcv_dict[ticker]["Adj Close"][i-1] / (ohlcv_dict[ticker]["ATR"][i-1] + ohlcv_dict[ticker]["Adj Close"][i-1])) - 1)
            #the buy signal is met(price goes up all of a sudden)
            elif ohlcv_dict[ticker]["High"][i] >= ohlcv_dict[ticker]["rolling_high_max"][i] and \
               ohlcv_dict[ticker]["Volume"][i] > 1.5 * ohlcv_dict[ticker]["rolling_max_vol"][i-1]:
                   signal[ticker] = "buy"
  
                   return_value[ticker].append((ohlcv_dict[ticker]["rolling_high_max"][i] / ohlcv_dict[ticker]["Adj Close"][i-1]) - 1)
            else:
                
                return_value[ticker].append((ohlcv_dict[ticker]["Adj Close"][i] / ohlcv_dict[ticker]["Adj Close"][i-1]) - 1)
            
    ohlcv_dict[ticker]["ret"] = np.array(return_value[ticker])
    
    
# calculating overall strategy's KPIs
strategy_df = pd.DataFrame()
for ticker in tickers:
    strategy_df[ticker] = ohlcv_dict[ticker]["ret"]
strategy_df["ret"] = strategy_df.mean(axis=1)
CAGR(strategy_df)
sharpe(strategy_df,0.025)
max_dd(strategy_df)  

# vizualization of strategy return
(1+strategy_df["ret"]).cumprod().plot()

#calculating individual stock's KPIs
cagr = {}
sharpe_ratios = {}
max_drawdown = {}
for ticker in tickers:
    print("calculating KPIs for ",ticker)      
    cagr[ticker] =  CAGR(ohlcv_dict[ticker])
    sharpe_ratios[ticker] =  sharpe(ohlcv_dict[ticker],0.025)
    max_drawdown[ticker] =  max_dd(ohlcv_dict[ticker])

KPI_df = pd.DataFrame([cagr,sharpe_ratios,max_drawdown],index=["Return","Sharpe Ratio","Max Drawdown"])      
KPI_df.T

