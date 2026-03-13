import credentials
from datetime import datetime, timedelta, time
import pandas as pd
import numpy as np
import pandas_ta as pdta
import talib as ta
import telegram_send
from time import sleep
from fyers_api import fyersModel

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

app_id = credentials.fyers_api2_id_BBP
app_secret = credentials.fyers_api2_secret_BBP
access_token = open("access_token2_BBP.txt", "r").read()
redirect_url = credentials.fyers_redirect_url
password = credentials.fyers_pwd_BBP
two_fa = credentials.fyers_two_fa_BBP
user_id = credentials.fyers_user_id_BBP
TimeFrame = 15
# now = pd.Timestamp.now(tz='Asia/Kolkata')
# trade_time = now.replace(hour=12, minute=30, second=0, microsecond=0)
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


def getHistoricalData(symbol, resolution=30):
    from_date = datetime.now()-timedelta(days=10)
    to_date = datetime.now()+timedelta(days=1)
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
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df = pd.DataFrame(candle_json['candles'], columns=columns)
    df['timestamp'] = (
        pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
    # df['symbol'] = symbol
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    df['time'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M')
    df = df[['symbol', 'date', 'time', 'timestamp', 'open', 'high', 'low', 'close', 'volume']]
    df.drop('timestamp', axis=1, inplace=True)
    # df['qty'] = credentials.N50_FUT_LOTSIZE[symbol]
    df['RSI'] = ta.RSI(df.close, timeperiod=14)
    df["REMA_9"] = ta.EMA(df['RSI'], timeperiod=20)
    df['CMF'] = pdta.cmf(df.high, df.low, df.close, df.volume, open_=None, lenght=None, offset=None)
    df["CSMA_20"] = ta.MA(df['CMF'], timeperiod=20)
    df['VWAP'] = pdta.vwap(high=df.high, low=df.low, close=df.close, volume=df.volume, anchor=None, offset=None)
    # df["volatility"] = round((df["high"]-df["low"]) * 100 / df["open"], 2)
    df['BUY'] = df['SELL'] = 0
    df = df.round(decimals=2)

    for i in range(20, len(df)):
        if df['close'][i] > df['VWAP'][i] and df['RSI'][i-1] <= df["RSMA_9"][i-1] and df['RSI'][i] > df["RSMA_9"][i] and df['CMF'][i] > df["CSMA_20"][i]:
            df['BUY'].at[i] = 1
        if df['close'][i] < df['VWAP'][i] and df['RSI'][i-1] >= df["RSMA_9"][i-1] and df['RSI'][i] < df["RSMA_9"][i] and df['CMF'][i] < df["CSMA_20"][i]:
            df['SELL'].at[i] = 1
    df.to_csv("D:/bhave/Desktop/1.csv", mode='a', header=True, index=False)
    return df


def checkSignal():
    while time(9, 15) <= pd.Timestamp.now(tz='Asia/Kolkata').time() <= time(23, 15):
        timenow = pd.Timestamp.now(tz='Asia/Kolkata')
        check = True if int(timenow.minute) / TimeFrame in list(np.arange(0.0, 4.0)) else False
        if check:
            nextscan = timenow+timedelta(minutes=TimeFrame)
            for symbol in SYMBOL_LIST:
                print(symbol)
                candle_df = getHistoricalData(symbol)
                if candle_df is not None:
                    latest_candle = candle_df.iloc[-1]
                    if latest_candle['BUY'] == 1:
                        Side = 1
                        ltp = latest_candle['close']
                        StopPrice = round(latest_candle['high'], 1)
                        LimitPrice = round(StopPrice+0.05, 2)
                        SL = round(0.003 * latest_candle['close'], 1)
                        Target = round(0.005 * latest_candle['close'], 1)
                        Qty = credentials.N50_FUT_LOTSIZE[symbol]

                        # place_order(symbol, qty=Qty, side=Side, stopLoss=SL, limitPrice=LimitPrice, takeProfit=Target, stopPrice=StopPrice)
                        # telegram_send.send(messages=[f"BUY {symbol}\n{datetime.now()}"])
                        print(f"Buy {symbol}\n{datetime.now()}")

                    if latest_candle['SELL'] == 1:
                        Side = -1
                        ltp = latest_candle['close']
                        StopPrice = round(latest_candle['low'], 1)
                        LimitPrice = round(StopPrice-0.05, 2)
                        SL = round(0.003 * latest_candle['close'], 1)
                        Target = round(0.005 * latest_candle['close'], 1)
                        Qty = credentials.N50_FUT_LOTSIZE[symbol]

                        # place_order(symbol, qty=Qty, side=Side, stopLoss=SL, limitPrice=LimitPrice, takeProfit=Target, stopPrice=StopPrice)
                        # telegram_send.send(messages=[f"SELL {symbol}\n{datetime.now()}"])
                        print(f"Sell {symbol}\n{datetime.now()}")
            waitsecs = int((nextscan-pd.Timestamp.now(tz='Asia/Kolkata')).seconds)
            print(pd.Timestamp.now(tz='Asia/Kolkata'))
            print("wait for {0} seconds".format(waitsecs))
            sleep(waitsecs) if waitsecs > 0 else sleep(0)
    else:
        ToDay = pd.Timestamp.now(tz='Asia/Kolkata')
        NextDay = ToDay + timedelta(days=1)
        NextDay_Start = NextDay.replace(hour=9, minute=15, second=0, microsecond=0)
        GoodNight = (NextDay_Start - ToDay).total_seconds()
        print(f" sleep for {GoodNight}")
        sleep(GoodNight) # 65760 at 9:16()


if __name__ == '__main__':
    fyers = fyersModel.FyersModel(client_id=app_id, token=access_token, log_path="D:\\bhave\\Desktop")
    checkSignal()
