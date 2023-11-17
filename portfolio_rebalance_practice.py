import financial_tools as ft
import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
import matplotlib.pyplot as plt

def CAGR(DF):
    "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
    df = DF.copy()
    df["cum_return"] = (1 + df["monthly_return"]).cumprod()
    n = len(df)/12
    CAGR = (df["cum_return"].tolist()[-1])**(1/n) - 1
    return CAGR

def volatility(DF):
    "function to calculate annualized volatility of a trading strategy"
    df = DF.copy()
    vol = df["monthly_return"].std() * np.sqrt(12)
    return vol

def sharpe(DF,rf):
    "function to calculate sharpe ratio ; rf is the risk free rate"
    df = DF.copy()
    sr = (CAGR(df) - rf)/volatility(df)
    return sr

def max_dd(DF):
    "function to calculate max drawdown"
    df = DF.copy()
    df["cum_return"] = (1 + df["monthly_return"]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd

'''tickers = ["MMM","AXP","T","BA","CAT","CSCO","KO", "XOM","GE","GS","HD",
           "IBM","INTC","JNJ","JPM","MCD","MRK","MSFT","NKE","PFE","PG","TRV",
           "UNH","VZ","V","WMT","DIS"]'''

tickers = ["MMM","AXP","T","BA","CAT","CSCO"]
ohlcv_mon_data = {}
start = dt.date.today() - dt.timedelta(3650)
end = dt.date.today()

for ticker in tickers:
    ohlcv_mon_data[ticker] = yf.download(ticker, start, end, interval="1mo")

ohlcv_mon_data[ticker].dropna(how="any", inplace = True)

#get the monthly return for tickets
copy_dict = ohlcv_mon_data.copy()
monthly_return = pd.DataFrame()
for ticker in tickers:
    copy_dict[ticker]["m_r"] = copy_dict[ticker]["Adj Close"].pct_change()
    monthly_return[ticker] = copy_dict[ticker]["m_r"]

monthly_return.dropna(how = "any", inplace = True)

def mon_portfolio(DF, total, delete):
    df = DF.copy()
    portfolio_list = []
    portfolio_return = [0]

    for i in range(len(df)):
        if len(portfolio_list) > 0:
            portfolio_return.append(df[portfolio_list].iloc[i,:].mean())
            bad_tickets = df[portfolio_list].iloc[i,:].sort_values(ascending = True)[:delete].index.values.tolist()
            #update the portfolio tickers (remove the last three tickers) 
            portfolio_list = [t for t in portfolio_list if t not in bad_tickets]
        #append tickets into portfolio
        append_num = total - len(portfolio_list)
        new_pick = df.iloc[i,:].sort_values(ascending = False)[:append_num].index.values.tolist()

        #update the portfolio by getting two lists together
        portfolio_list += new_pick

    monthly_return_df =pd.DataFrame(np.array(portfolio_return), columns=["monthly_return"]) 
    return monthly_return_df

CAGR(mon_portfolio(monthly_return,6,3))
sharpe(mon_portfolio(monthly_return,6,3),0.025)
max_dd(mon_portfolio(monthly_return,6,3)) 


#calculating KPIs for Index buy and hold strategy over the same period
DJI = yf.download("^DJI",dt.date.today()-dt.timedelta(3650),dt.date.today(),interval='1mo')
DJI["monthly_return"] = DJI["Adj Close"].pct_change().dropna(how = "any")
CAGR(DJI)
sharpe(DJI,0.025)
max_dd(DJI)


#visualization
fig, ax = plt.subplots()
plt.plot((1+mon_portfolio(monthly_return,6,3)).cumprod())
plt.plot((1+DJI["monthly_return"].reset_index(drop=True)).cumprod())
plt.title("Index Return vs Strategy Return")
plt.ylabel("cumulative return")
plt.xlabel("months")
ax.legend(["Strategy Return","Index Return"])
