# Trading-Algorithm-Script
Python script of several different stock trading strategies 

Overview
These Python scripts implement several simple trading strategy backtesting tool using historical stock price data. The strategeis involve several charts or signals to generate buy and sell signals.


Functions:
## Renko_macd
- `MACD(DF, a, b, c)`: Calculate MACD and Signal Line.
- `ATR(DF, n)`: Calculate True Range and Average True Range.
- `slope(ser, n)`: Calculate the slope of n consecutive points on a plot.
- `renko_DF(DF)`: Convert OHLC data into Renko bricks.
- `CAGR(DF)`: Calculate the Cumulative Annual Growth Rate of a trading strategy.
- `volatility(DF)`: Calculate annualized volatility of a trading strategy.
- `sharpe(DF, rf)`: Calculate the Sharpe ratio; rf is the risk-free rate.
- `max_dd(DF)`: Calculate the maximum drawdown.

## Portfolio_rebalance
- `CAGR(DF)`: Calculate the Cumulative Annual Growth Rate of a trading strategy.
- `volatility(DF)`: Calculate annualized volatility of a trading strategy.
- `sharpe(DF, rf)`: Calculate the Sharpe ratio; rf is the risk-free rate.
- `max_dd(DF)`: Calculate the maximum drawdown.
- Download monthly historical data for selected stocks.
- Calculate monthly returns.
- `mon_portfolio(DF, total, delete)`: Calculate returns for a portfolio strategy.

## Resistance breakout
- `CAGR(DF)`: Calculate the Cumulative Annual Growth Rate of a trading strategy.
- `volatility(DF)`: Calculate annualized volatility of a trading strategy.
- `sharpe(DF, rf)`: Calculate the Sharpe ratio; rf is the risk-free rate.
- `max_dd(DF)`: Calculate the maximum drawdown.
- `ATR(DF, n)`: Calculate True Range and Average True Range.
- Download historical data (monthly) for selected stocks.
- Calculate ATR and rolling max price.
- Implement a trading strategy and calculate returns.

## Renko_OBV
- `ATR(DF, n)`: Calculate True Range and Average True Range.
- `slope(ser, n)`: Calculate the slope of n consecutive points on a plot.
- `renko_DF(DF)`: Convert OHLC data into Renko bricks.
- `OBV(DF)`: Calculate On Balance Volume.
- `CAGR(DF)`: Calculate the Cumulative Annual Growth Rate of a trading strategy.
- `volatility(DF)`: Calculate annualized volatility of a trading strategy.
- `sharpe(DF, rf)`: Calculate the Sharpe ratio; rf is the risk-free rate.
- `max_dd(DF)`: Calculate the maximum drawdown.
- Download historical data for DJI constituent stocks.
- Merge Renko data with original OHLC data.
- Implement a trading strategy using Renko and OBV indicators.
