from time import sleep, time, strftime, localtime

import credentials
from datetime import datetime, timedelta
import pandas as pd
import pandas_ta as pdta
import talib as ta
import threading
import telegram_send
from fyers_api import fyersModel

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

app_id = credentials.api_id
app_secret = credentials.api_secret
redirect_url = credentials.Fyers_redirect_url
password = credentials.pwd
two_fa = credentials.two_fa
user_id = credentials.user_id
access_token = open("access_token_BBP.txt", "r").read()
SYMBOL_LIST = credentials.N_OPTION

TRADED_SYMBOL = []
timeFrame = 300
StartTime = datetime.strptime("2021-09-29 9:55:0", "%Y-%m-%d %H:%M:%S")


def calculate_indicator(res_json):
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df = pd.DataFrame(res_json['candles'], columns=columns)
    df['timestamp'] = (pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    df['time'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M')
    df = df[['date', 'time', 'timestamp', 'open', 'high', 'low', 'close', 'volume']]
    df.drop('timestamp', axis=1, inplace=True)
    df.set_index(pd.DatetimeIndex(df["date"]), inplace=True)
    df.drop('date', axis=1, inplace=True)
    df['VWAP'] = pdta.vwap(high=df.high, low=df.low, close=df.close, volume=df.volume, anchor=None, offset=None)
    df.reset_index(inplace=True)
    df["VSMA_20"] = ta.SMA(df.volume, timeperiod=20)
    df["RSI_14"] = ta.RSI(df.close, timeperiod=14)
    df['CROSS_UP'] = 0
    df = df.round(decimals=2)

    for i in range(30, len(df)):
        if df['RSI_14'][i] > 60 and df['close'][i] > df['VSMA_20'][i] and df['volume'][i] > df['VSMA_20'][i]:
            df['CROSS_UP'].at[i] = 1
    # print(df.tail(2))
    return df


def getHistoricalData(symbol=SYMBOL_LIST, resolution=5):
    from_date = datetime.now() - timedelta(days=4)
    to_date = datetime.now() + timedelta(days=1)
    from_date_format = from_date.strftime("%Y-%m-%d")
    to_date_format = to_date.strftime("%Y-%m-%d")
    data = {
        "symbol": symbol,
        "resolution": resolution,
        "date_format": 1,
        "range_from": from_date_format,
        "range_to": to_date_format,
        "cont_flag": 1
    }
    candle_json = fyers.history(data)
    return calculate_indicator(candle_json)


def checkSignal():
    start = time()
    global TRADED_SYMBOL

    for symbol in SYMBOL_LIST:
        print(symbol)
        candel_df = getHistoricalData(symbol)
        if candel_df is not None:
            latest_candel = candel_df.iloc[-1]

            if latest_candel['CROSS_UP'] == 1:
                ltp = latest_candel['close']

                telegram_send.send(messages=[
                    f"Option_BOT\nBuy:\n{symbol}\nEntry Price: {ltp}\n{datetime.now().time()}"])
                print(f'Buy {symbol} Entry Price: {ltp} at{datetime.now()}')


    interval = timeFrame - (time() - start)
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()))
    print(interval)
    threading.Timer(interval, checkSignal).start()


if __name__ == '__main__':
    fyers = fyersModel.FyersModel(client_id=app_id, token=access_token, log_path="E:\\bhave\\Desktop")
    interval = StartTime - datetime.now()
    print(f"Code run after {interval.total_seconds() if interval.total_seconds() > 0 else sleep(0)} sec")
    sleep(interval.total_seconds()) if interval.total_seconds() > 0 else sleep(0)
    checkSignal()
