import threading
from datetime import timedelta, datetime
import pandas as pd
import pandas_ta as pdta
import talib as ta
import telegram_send
from time import sleep, time

import fy_lib

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

TimeFrame = 900
now = datetime.now()
trade_time = now.replace(hour=13, minute=45, second=0, microsecond=0)

SYMBOL_LIST = [name[:-3]+ '21NOVFUT' for name in fy_lib.N50_LIST]


def historicalData(symbol, resolution=15):
    df = fy_lib.historical_data(symbol, delta=5, resolution=resolution)
    df.set_index(pd.DatetimeIndex(df["timestamp"]), inplace=True)
    df['VWAP'] = pdta.vwap(df.high, df.low, df.close, df.volume, anchor=None, offset=None)
    df['RSI'] = ta.RSI(df.close, timeperiod=14)
    df["REMA_9"] = ta.EMA(df['RSI'], timeperiod=9)
    df['OBV'] = ta.OBV(df.close, df.volume)
    df["OSMA_20"] = ta.MA(df['OBV'], timeperiod=20)
    df['ST'] = pdta.supertrend(high=df.high, low=df.low, close=df.close, period=7, multiplier=2)['SUPERT_7_2.0']
    df['BUY'] = df['SELL'] = df['V_DOWN'] = df['V_UP'] = 0
    df = df.round(decimals=2)
    for i in df.timestamp:
        if df['close'][i] < df['VWAP'][i]:
            df['V_DOWN'].at[i] = 1
        if df['close'][i] > df['VWAP'][i]:
            df['V_UP'].at[i] = 1
        if df['close'][i] > df['VWAP'][i] and df['RSI'][i] > df["REMA_9"][i] and df['OBV'][i] > df["OSMA_20"][i] and \
                df['close'][i] > df['ST'][i]:
            df['BUY'].at[i] = 1
        if df['close'][i] < df['VWAP'][i] and df['RSI'][i] < df["REMA_9"][i] and df['OBV'][i] < df["OSMA_20"][i] and \
                df['close'][i] < df['ST'][i]:
            df['SELL'].at[i] = 1
    print(df.tail(2))
    # df.to_csv("D:/bhave/Desktop/2.csv", mode='a', header=True, index=False)
    return df


def checkSignal():
    start = time()
    print(datetime.fromtimestamp(start).strftime('%Y-%m-%d %H:%M:%S'))
    for symbol in SYMBOL_LIST:
        lt = (pd.Timestamp.now(tz='Asia/Kolkata')-timedelta(minutes=15)).replace(second=0, microsecond=0)
        pt = (pd.Timestamp.now(tz='Asia/Kolkata')-timedelta(minutes=30)).replace(second=0, microsecond=0)
        candle_df = historicalData(symbol)
        if candle_df is not None:
            prev_candle = candle_df.loc[pt]
            latest_candle = candle_df.loc[lt]
            if prev_candle['V_DOWN'] == 1 and latest_candle['BUY'] == 1:
                telegram_send.send(messages=[f"BUY {symbol}\n{datetime.now()}"])
                print(f"Buy {symbol}\n{datetime.now()}")
            if prev_candle['V_UP'] == 1 and latest_candle['SELL'] == 1:
                telegram_send.send(messages=[f"SELL {symbol}\n{datetime.now()}"])
                print(f"Sell {symbol}\n{datetime.now()}")
    Interval = TimeFrame-(time()-start)
    print(f"Next Scan {(pd.Timestamp.now(tz='Asia/Kolkata')+timedelta(minutes=15)).replace(second=0, microsecond=0)}")
    threading.Timer(Interval, checkSignal).start()


if __name__ == '__main__':
    interval = trade_time-now
    print(f"Code run after {interval.total_seconds()} sec")
    sleep(interval.total_seconds()) if interval.total_seconds() > 0 else sleep(0)
    checkSignal()
