from time import sleep, time, strftime, localtime
import credentials
from datetime import datetime, timedelta
import pandas as pd
import talib as ta
import pandas_ta as pdta
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
SYMBOL_LIST = ["NSE:NIFTY21SEPFUT", "NSE:BANKNIFTY21SEPFUT"]

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
    df['CMF_20'] = pdta.cmf(df.high, df.low, df.close, df.volume, open_=None, lenght=None, offset=None)
    df["RSI_14"] = ta.RSI(df.close, timeperiod=14)
    df['MFI_14'] = ta.MFI(df.high, df.low, df.close, df.volume, timeperiod=14)
    df['CROSS_UP'] = df['CROSS_DOWN'] = 0
    df = df.round(decimals=2)

    for i in range(30, len(df)):
        if df['CMF_20'][i] > 0 and df["RSI_14"][i] > 60 and df['MFI_14'][i] > 60:
            df['CROSS_UP'].at[i] = 1
        if df['CMF_20'][i] < 0 and df["RSI_14"][i] < 40 and df['MFI_14'][i] < 40:
            df['CROSS_DOWN'].at[i] = 1
    # print(df.tail(3))
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
        # print(symbol)
        candel_df = getHistoricalData(symbol)
        if candel_df is not None:
            latest_candel = candel_df.iloc[-1]

            if latest_candel['CROSS_UP'] == 1:
                telegram_send.send(messages=[f"INDEX_BOT\nBuy:\n{symbol}\n{datetime.now().time()}"])
                print(f'Buy {symbol} at{datetime.now()}')

            if latest_candel['CROSS_DOWN'] == 1:
                telegram_send.send(messages=[f"INDEX_BOT\nSell:\n{symbol}\n{datetime.now().time()}"])
                print(f'Sell {symbol} at{datetime.now()}')

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