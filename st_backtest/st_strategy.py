import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from math import floor

import st
from termcolor import colored as cl

import fy_lib

plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = (20,10)


A_port = fy_lib.historical_data("NSE:ADANIPORTS21NOVFUT", delta=5, resolution='D')
st = st.get_supertrend(high=A_port.high, low=A_port.low, close=A_port.close, lookback=7, multiplier=2)['st']


def implement_st_strategy(prices, st):
    buy_price = []
    sell_price = []
    st_signal = []
    signal = 0

    for i in range(len(st)):
        if st[i-1] > prices[i-1] and st[i] < prices[i]:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                st_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                st_signal.append(0)
        elif st[i-1] < prices[i-1] and st[i] > prices[i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                st_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                st_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            st_signal.append(0)

    return buy_price, sell_price, st_signal

buy_price, sell_price, st_signal = implement_st_strategy(A_port.close, st=st)

plt.plot(A_port['close'], linewidth = 2)
plt.plot(A_port['st'], color = 'green', linewidth = 2, label = 'ST UPTREND')
plt.plot(A_port['st_dt'], color = 'r', linewidth = 2, label = 'ST DOWNTREND')
plt.plot(A_port.index, buy_price, marker = '^', color = 'green', markersize = 12, linewidth = 0, label = 'BUY SIGNAL')
plt.plot(A_port.index, sell_price, marker = 'v', color = 'r', markersize = 12, linewidth = 0, label = 'SELL SIGNAL')
plt.title('A_port ST TRADING SIGNALS')
plt.legend(loc = 'upper left')
plt.show()

position = []
for i in range(len(st_signal)):
    if st_signal[i] > 1:
        position.append(0)
    else:
        position.append(1)

for i in range(len(A_port['close'])):
    if st_signal[i] == 1:
        position[i] = 1
    elif st_signal[i] == -1:
        position[i] = 0
    else:
        position[i] = position[i-1]

close_price = A_port['close']
st = A_port['st']
st_signal = pd.A_portFrame(st_signal).rename(columns={0: 'st_signal'}).set_index(A_port.index)
position = pd.A_portFrame(position).rename(columns={0: 'st_position'}).set_index(A_port.index)

frames = [close_price, st, st_signal, position]
strategy = pd.concat(frames, join='inner', axis=1)

A_port_ret = pd.A_portFrame(np.diff(A_port['close'])).rename(columns={0: 'returns'})
st_strategy_ret = []

for i in range(len(A_port_ret)):
    returns = A_port_ret['returns'][i] * strategy['st_position'][i]
    st_strategy_ret.append(returns)

st_strategy_ret_df = pd.A_portFrame(st_strategy_ret).rename(columns={0: 'st_returns'})
investment_value = 100000
number_of_stocks = floor(investment_value / A_port['close'][-1])
st_investment_ret = []

for i in range(len(st_strategy_ret_df['st_returns'])):
    returns = number_of_stocks * st_strategy_ret_df['st_returns'][i]
    st_investment_ret.append(returns)

st_investment_ret_df = pd.A_portFrame(st_investment_ret).rename(columns={0: 'investment_returns'})
total_investment_ret = round(sum(st_investment_ret_df['investment_returns']), 2)
profit_percentage = floor((total_investment_ret / investment_value) * 100)
print(cl('Profit gained from the ST strategy by investing $100k in A_port : {}'.format(total_investment_ret),
         attrs=['bold']))
print(cl('Profit percentage of the ST strategy : {}%'.format(profit_percentage), attrs=['bold']))
