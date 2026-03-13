from time import sleep, time, strftime, localtime

import credentials
from datetime import datetime, timedelta
import telegram_send
import pandas as pd
import talib as ta
import pandas_ta as pdta
import threading
from fyers_api import fyersModel

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

app_id = credentials.Fyers_api_id_BBP
app_secret = credentials.Fyers_api_secret_BBP
password = credentials.Fyers_pwd_BBP
two_fa = credentials.Fyers_two_fa_BBP
user_id = credentials.Fyers_user_id_BBP

redirect_url = credentials.Fyers_redirect_url
access_token = open("access_token_BBP.txt", "r").read()

SYMBOL_LIST = credentials.N50_FUT_LIST
timeFrame = 300
StartTime = datetime.strptime("2021-10-06 9:30:0", "%Y-%m-%d %H:%M:%S")


def calculate_indicator(res_json):
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df = pd.DataFrame(res_json['candles'], columns=columns)
    df['timestamp'] = (pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    df['time'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M')
    df = df[['date', 'time', 'timestamp', 'open', 'high', 'low', 'close', 'volume']]
    df.drop('timestamp', axis=1, inplace=True)
    df["RSI_14"] = ta.RSI(df.close, timeperiod=14)
    df['ST'] = pdta.supertrend(high= df.high, low= df.low, close= df.close, period=10, multiplier=3)['SUPERT_7_3.0']
    df["BBU"], df["BBM"], df["BBL"] = ta.BBANDS(df.close, timeperiod=20, nbdevup=2, nbdevdn=2)
    df['Buy'] = df['Sell'] = 0

    df = df.round(decimals=2)

    for i in range(30, len(df)):
        if df['RSI_14'][i] > 60 and df['close'][i-1] < df['ST'][i-1] <= df['close'][i] and df['close'][i] > df['BBM'][i]:
            df['Buy'].at[i] = 1
        if df['RSI_14'][i] < 40 and df['close'][i-1] > df['ST'][i-1] >= df['close'][i] and df['close'][i] < df['BBM'][i]:
            df['Sell'].at[i] = 1
    print(df.tail(2))
    return df


def getHistoricalData(symbol=SYMBOL_LIST, resolution=5):
    from_date = datetime.now() - timedelta(days=10)
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
            previ_candel = candel_df.iloc[-2]
            latest_candel = candel_df.iloc[-1]

            if latest_candel['Buy'] == 1:
                ltp = latest_candel['close']

                telegram_send.send(messages=[
                    f"RSI_BOT\nBuy:\n{symbol}\nEntry Price: {ltp}\n{datetime.now().time()}"])
                print(f'Buy {symbol} Stop Price {ltp} at{datetime.now()}')

            if latest_candel['Sell'] == 1:
                ltp = latest_candel['close']

                telegram_send.send(messages=[
                    f"RSI_BOT\nSell:\n{symbol}\nEntry Price: {ltp}\n{datetime.now().time()}"])
                print(f'Sell {symbol} Stop Price {ltp} at{datetime.now()}')

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

