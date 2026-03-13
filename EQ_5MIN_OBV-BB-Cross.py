from datetime import timedelta, datetime, time
import numpy as np
import pandas as pd
import pandas_ta as pdta
import talib as ta
import telegram_send
from time import sleep
from api_helper import ShoonyaApiPy

from fy_lib import historical_data, N50

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

TimeFrame = 5
SYMBOL_LIST = ['NSE:' + name + '21DECFUT' for name in N50]


def historicalData(symbol, resolution=5):
    df = historical_data(symbol, delta=5, resolution=resolution)
    df.set_index(pd.DatetimeIndex(df["timestamp"]), inplace=True)
    df['OBV'] = ta.OBV(df.close, df.volume)
    df['OBBU'], df['OBBM'], df['OBBL'] = ta.BBANDS(df['OBV'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df['BBU'], df['BBM'], df['BBL'] = ta.BBANDS(df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df['O_DOWN'] = df['O_UP'] = 0
    df = df.round(decimals=2)
    for i in df.timestamp:
        if df['OBV'][i] < df["OBBL"][i] and df["close"][i] < df["BBL"][i]:
            df['O_DOWN'].at[i] = 1
        if df['OBV'][i] > df["OBBU"][i] and df["close"][i] > df["BBU"][i]:
            df['O_UP'].at[i] = 1
    print(df.tail(3))
    # df.to_csv("D:/bhave/Desktop/2.csv", mode='a', header=True, index=False)
    return df

api = ShoonyaApiPy()
def checkSignal():
    while time(9, 15) <= pd.Timestamp.now(tz='Asia/Kolkata').time() <= time(23, 15):
        timenow = pd.Timestamp.now(tz='Asia/Kolkata')
        check = True if int(timenow.minute) / TimeFrame in list(np.arange(0.0, 11.0)) else False
        if check:
            nextscan = timenow+timedelta(minutes=TimeFrame)
            for symbol in SYMBOL_LIST:
                print(symbol)
                lt = (pd.Timestamp.now(tz='Asia/Kolkata')-timedelta(minutes=5)).replace(second=0, microsecond=0)
                pt = (pd.Timestamp.now(tz='Asia/Kolkata')-timedelta(minutes=10)).replace(second=0, microsecond=0)
                candle_df = historicalData(symbol)
                if candle_df is not None:
                    prev_candle = candle_df.loc[pt]
                    latest_candle = candle_df.loc[lt]

                    if latest_candle['O_UP'] == 1:
                        telegram_send.send(messages=[f"OBV.Cross-BUY {symbol}\n{datetime.now()}"])
                        print(f"OBV-Buy {symbol}\n{datetime.now()}")
                    api.place_order(buy_or_sell='B', product_type='C',
                                    exchange='NSE', tradingsymbol='INFY-EQ',
                                    quantity=1, discloseqty=0, price_type='LMT', price=1500.00, trigger_price=None,
                                    retention='DAY', remarks='my_order_001')

                    if latest_candle['O_DOWN'] == 1:
                        telegram_send.send(messages=[f"OBV.Cross-SELL {symbol}\n{datetime.now()}"])
                        print(f"OBV-Sell {symbol}\n{datetime.now()}")


            waitsecs = int((nextscan-pd.Timestamp.now(tz='Asia/Kolkata')).seconds)
            print(f"Next Scan {nextscan.replace(second=0, microsecond=0)}")
            sleep(waitsecs) if waitsecs > 0 else sleep(0)


if __name__ == '__main__':
    checkSignal()
