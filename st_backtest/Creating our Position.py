import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from math import floor
from termcolor import colored as cl

plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = (20,10)

position = []
for i in range(len(st_signal)):
    if st_signal[i] > 1:
        position.append(0)
    else:
        position.append(1)

for i in range(len(tsla['close'])):
    if st_signal[i] == 1:
        position[i] = 1
    elif st_signal[i] == -1:
        position[i] = 0
    else:
        position[i] = position[i-1]

close_price = tsla['close']
st = tsla['st']
st_signal = pd.DataFrame(st_signal).rename(columns={0: 'st_signal'}).set_index(tsla.index)
position = pd.DataFrame(position).rename(columns={0: 'st_position'}).set_index(tsla.index)

frames = [close_price, st, st_signal, position]
strategy = pd.concat(frames, join='inner', axis=1)

strategy