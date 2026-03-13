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

app_id = credentials.fyers_api2_id_BBP
app_secret = credentials.fyers_api2_secret_BBP
redirect_url = credentials.fyers_redirect_url
password = credentials.fyers_pwd_BBP
two_fa = credentials.fyers_two_fa_BBP
user_id = credentials.fyers_user_id_BBP
access_token = open("access_token2_BBP.txt", "r").read()
SYMBOL_LIST = credentials.N50_LIST

TRADED_SYMBOL = []
timeFrame = 300
StartTime = datetime.strptime("2021-11-12 11:10:0", "%Y-%m-%d %H:%M:%S")


def calculate_indicator(res_json):
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df = pd.DataFrame(res_json['candles'], columns=columns)
    df['timestamp'] = (pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    df['time'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M')
    df = df[['date', 'time', 'timestamp', 'open', 'high', 'low', 'close', 'volume']]
    df['CMF_20'] = pdta.cmf(df.high, df.low, df.close, df.volume, open_=None, lenght=None, offset=None)
    df["RSI_14"] = ta.RSI(df.close, timeperiod=14)
    df['ATR_14'] = ta.ATR(df.high, df.low, df.close, timeperiod=20)
    df["MACD"], df["MACD_S"], df["MACD_H"] = ta.MACD(df.close, fastperiod=12, slowperiod=26, signalperiod=9)
    df.drop(['timestamp', "MACD_S", "MACD"], axis=1, inplace=True)
    df['BUY'] = df['SELL'] = 0
    df = df.round(decimals=2)

    for i in range(30, len(df)):
        if df['CMF_20'][i] > 0.1 and df["RSI_14"][i] > 60 and df['MACD_H'][i] > 0:
            df['BUY'].at[i] = 1
        if df['CMF_20'][i] < -0.1 and df["RSI_14"][i] < 40 and df['MACD_H'][i] < 0:
            df['SELL'].at[i] = 1
    print(df.tail(3))
    return df


def getHistoricalData(symbol=SYMBOL_LIST, resolution=5):
    from_date = datetime.now() - timedelta(days=2)
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
            prev_candel = candel_df.iloc[-2]
            latest_candel = candel_df.iloc[-1]

            if latest_candel['BUY'] == 1:
                ltp = latest_candel['close']
                StopPrice = latest_candel['high']
                SL = round(2 * latest_candel['ATR_14'], 1)
                Target = round(4 * latest_candel['ATR_14'], 1)
                Qty = round(50000 / ltp, 0)

                # telegram_send.send(messages=[f"MFI_CMI_RSI\nBuy:\n{symbol}\nEntry Price: {StopPrice}\nSL: {SL}\nTGT: {Target}\nQTY: {Qty}\n{datetime.now().time()}"])
                print(f'Buy {symbol} Stop Price {StopPrice}  SL {SL}  TGT {Target} QTY {Qty} at{datetime.now()}')
                # TRADED_SYMBOL.append(symbol)

            if latest_candel['SELL'] == 1:
                ltp = latest_candel['close']
                StopPrice = latest_candel['low']
                SL = round(2 * latest_candel['ATR_14'], 1)
                Target = round(4 * latest_candel['ATR_14'], 1)
                Qty = round(50000 / ltp, 0)

                # telegram_send.send(messages=[f"MFI_CMI_RSI\nSell:\n{symbol}\nEntry Price: {StopPrice}\nSL: {SL}\nTGT: {Target}\nQTY: {Qty}\n{datetime.now().time()}"])
                print(f'Sell {symbol} Stop Price {StopPrice}  SL {SL}  TGT {Target} QTY {Qty} at{datetime.now()}')
                # TRADED_SYMBOL.append(symbol)
    interval = timeFrame - (time() - start)
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()))
    print(interval)
    threading.Timer(interval, checkSignal).start()


if __name__ == '__main__':
    fyers = fyersModel.FyersModel(client_id=app_id, token=access_token, log_path="D:\\bhave\\Desktop")
    interval = StartTime - datetime.now()
    print(f"Code run after {interval.total_seconds() if interval.total_seconds() > 0 else sleep(0)} sec")
    sleep(interval.total_seconds()) if interval.total_seconds() > 0 else sleep(0)
    checkSignal()
