import credentials
from datetime import datetime, timedelta
import pandas as pd
import pandas_ta as pdta
import talib as ta
import telegram_send
import threading
from time import time, sleep, strftime, localtime
from fyers_api import fyersModel

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

app_id = credentials.fyers_api_id_BBP
app_secret = credentials.fyers_api_secret_BBP
redirect_url = credentials.fyers_redirect_url
password = credentials.fyers_pwd_BBP
two_fa = credentials.fyers_two_fa_BBP
user_id = credentials.fyers_user_id_BBP
access_token = open("access_token_BBP.txt", "r").read()
TimeFrame = 900
now = pd.Timestamp.now(tz='Asia/Kolkata')
start_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
trade_time = now.replace(hour=14, minute=30, second=0, microsecond=0)
stop_time = now.replace(hour=15, minute=0, second=0, microsecond=0)
# StartTime = datetime.strptime("2021-10-01 09:20:0", "%Y-%m-%d %H:%M:%S")
SYMBOL_LIST = credentials.N50_FUT_LIST


def place_order(symbol, qty, side, stopPrice, limitPrice, stopLoss, takeProfit):
    data = {
        "symbol": symbol,
        "qty": qty,
        "type": 4,
        "side": side,
        "productType": "BO",
        "limitPrice": limitPrice,
        "stopPrice": stopPrice,
        "validity": "DAY",
        "disclosedQty": 0,
        "offlineOrder": "False",
        "stopLoss": stopLoss,
        "takeProfit": takeProfit
    }
    Rep = fyers.place_order(data)
    print("Order Status: {}".format(Rep["message"]))


def calculate_indicator(res_json):
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df = pd.DataFrame(res_json['candles'], columns=columns)
    df['timestamp'] = (pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    df['time'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M')
    df = df[['date', 'time', 'timestamp', 'open', 'high', 'low', 'close', 'volume']]
    df.drop('timestamp', axis=1, inplace=True)
    df [ 'RSI' ] = ta.RSI(df.close, timeperiod=14)
    df [ "RSMA_20" ] = ta.MA(df [ 'RSI' ], timeperiod=20)
    df [ 'CMF' ] = pdta.cmf(df.high, df.low, df.close, df.volume, open_=None, lenght=None, offset=None)
    df [ "CSMA_20" ] = ta.MA(df [ 'CMF' ], timeperiod=20)
    df [ "SMA_9" ] = ta.MA(df [ 'close' ], timeperiod=9)
    df['BUY'] = df['SELL'] = 0
    df = df.round(decimals=2)

    for i in range(20, len(df)):
        if df['RSI'][i-2] <= df["RSMA_20"][i-2] and df['RSI'][i-1] <= df["RSMA_20"][i-1] and df['RSI'][i] > df["RSMA_20"][i] and df['CMF'][i] > df["CSMA_20"][i] and df["close"][i] > df["SMA_9"][i]:
            df['BUY'].at[i] = 1
        if df['RSI'][i-2] >= df["RSMA_20"][i-2] and df['RSI'][i-1] >= df["RSMA_20"][i-1] and df['RSI'][i] < df["RSMA_20"][i] and df['CMF'][i] < df["CSMA_20"][i] and df["close"][i] < df["SMA_9"][i]:
            df['SELL'].at[i] = 1
    # print(df.tail(2))
    return df


def getHistoricalData(symbol, resolution= 15):
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
        for symbol in SYMBOL_LIST:
            # print(symbol)
            candle_df = getHistoricalData(symbol)
            if candle_df is not None:
                latest_candle = candle_df.iloc[-1]
                if latest_candle['BUY'] == 1:
                    Side = 1
                    ltp = latest_candle['close']
                    StopPrice = round(latest_candle['high'], 1)
                    LimitPrice = round(StopPrice + 0.05, 2)
                    SL = round(0.003 * latest_candle [ 'close' ], 1)
                    Target = round(0.005 * latest_candle [ 'close' ], 1)
                    Qty = credentials.N50_FUT_LOTSIZE[symbol]

                    # place_order(symbol, qty=Qty, side=Side, stopLoss=SL, limitPrice=LimitPrice, takeProfit=Target, stopPrice=StopPrice)
                    telegram_send.send(messages=[f"BUY {symbol}\n{datetime.now()}"])
                    print(f"Buy {symbol}\n{datetime.now()}")

                if latest_candle['SELL'] == 1:
                    Side = -1
                    ltp = latest_candle['close']
                    StopPrice = round(latest_candle['low'], 1)
                    LimitPrice = round(StopPrice - 0.05, 2)
                    SL = round(0.003 * latest_candle['close'], 1)
                    Target = round(0.005 * latest_candle['close'], 1)
                    Qty = credentials.N50_FUT_LOTSIZE[symbol]

                    # place_order(symbol, qty=Qty, side=Side, stopLoss=SL, limitPrice=LimitPrice, takeProfit=Target, stopPrice=StopPrice)
                    telegram_send.send(messages=[f"SELL {symbol}\n{datetime.now()}"])
                    print(f"Sell {symbol}\n{datetime.now()}")
        interval = TimeFrame - (time()-start)
        print(strftime("%Y-%m-%d %H:%M:%S", localtime()))
        print(interval)
        threading.Timer(interval, checkSignal).start()


if __name__ == '__main__':
    fyers = fyersModel.FyersModel(client_id=app_id, token=access_token, log_path="E:\\bhave\\Desktop")
    interval = trade_time - now
    print(f"Code run after {interval.total_seconds() if interval.total_seconds() > 0 else sleep(0)} sec")
    sleep(interval.total_seconds()) if interval.total_seconds() > 0 else sleep(0)
    checkSignal()
