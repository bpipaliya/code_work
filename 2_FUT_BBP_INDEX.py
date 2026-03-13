import threading
import credentials
from datetime import timedelta, datetime
import pandas as pd
import pandas_ta as pdta
import talib as ta
import telegram_send
from time import sleep, strftime, localtime, time
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

TimeFrame = 900
now = datetime.now()
trade_time = now.replace(hour=11, minute=15, second=0, microsecond=0)

SYMBOL_LIST = ["NSE:NIFTY21NOVFUT", "NSE:BANKNIFTY21NOVFUT"]


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


def getHistoricalData(symbol, resolution=15):
    from_date = datetime.now()-timedelta(days=5)
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
    df['timestamp'] = (pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    df['time'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M')
    df = df[['date', 'time', 'timestamp', 'open', 'high', 'low', 'close', 'volume']]
    df.drop('timestamp', axis=1, inplace=True)
    df.set_index(pd.DatetimeIndex(df["date"]), inplace=True)
    df.drop('date', axis=1, inplace=True)
    df['VWAP'] = pdta.vwap(df.high, df.low, df.close, df.volume, anchor=None, offset=None)
    df.reset_index(inplace=True)
    df['RSI'] = ta.RSI(df.close, timeperiod=14)
    df["REMA_9"] = ta.EMA(df['RSI'], timeperiod=9)
    df['OBV'] = ta.OBV(df.close, df.volume)
    df["OSMA_20"] = ta.MA(df['OBV'], timeperiod=20)
    df['ST']= pdta.supertrend(high=df.high, low=df.low, close=df.close, period=7, multiplier=2)['SUPERT_7_2.0']
    df['BUY'] = df['SELL'] = 0
    df = df.round(decimals=2)

    for i in range(20, len(df)):
        if df['close'][i-1] < df['VWAP'][i-1] and df['close'][i] > df['VWAP'][i] and df['RSI'][i] > df["REMA_9"][i] and \
                df['OBV'][i] > df["OSMA_20"][i]:
            df['BUY'].at[i] = 1
        if df['close'][i-1] > df['VWAP'][i-1] and df['close'][i] < df['VWAP'][i] and df['RSI'][i] < df["REMA_9"][i] and \
                df['OBV'][i] < df["OSMA_20"][i]:
            df['SELL'].at[i] = 1
    print(df.tail(5))
    # df.to_csv("D:/bhave/Desktop/2.csv", mode='a', header=True, index=False)
    return df


def checkSignal():
    start = time()
    print(datetime.fromtimestamp(start).strftime('%Y-%m-%d %H:%M:%S'))
    for symbol in SYMBOL_LIST:
        # print(symbol)
        candle_df = getHistoricalData(symbol)
        if candle_df is not None:
            latest_candle = candle_df.iloc[-2]
            if latest_candle['BUY'] == 1:
                # Side = 1
                # ltp = latest_candle['close']
                # StopPrice = round(latest_candle['high'], 1)
                # LimitPrice = round(StopPrice+0.05, 2)
                # SL = round(0.003 * latest_candle['close'], 1)
                # Target = round(0.005 * latest_candle['close'], 1)
                # Qty = credentials.N50_FUT_LOTSIZE[symbol]

                # place_order(symbol, qty=Qty, side=Side, stopLoss=SL, limitPrice=LimitPrice, takeProfit=Target, stopPrice=StopPrice)
                telegram_send.send(messages=[f"BUY {symbol}\n{datetime.now()}"])
                print(f"Buy {symbol}\n{datetime.now()}")

            if latest_candle['SELL'] == 1:
                # Side = -1
                # ltp = latest_candle['close']
                # StopPrice = round(latest_candle['low'], 1)
                # LimitPrice = round(StopPrice-0.05, 2)
                # SL = round(0.003 * latest_candle['close'], 1)
                # Target = round(0.005 * latest_candle['close'], 1)
                # Qty = credentials.N50_FUT_LOTSIZE[symbol]

                # place_order(symbol, qty=Qty, side=Side, stopLoss=SL, limitPrice=LimitPrice, takeProfit=Target, stopPrice=StopPrice)
                telegram_send.send(messages=[f"SELL {symbol}\n{datetime.now()}"])
                print(f"Sell {symbol}\n{datetime.now()}")

    interval = TimeFrame-(time()-start)
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()))
    print(f"Code run after {interval} sec")
    threading.Timer(interval, checkSignal).start()


if __name__ == '__main__':
    fyers = fyersModel.FyersModel(client_id=app_id, token=access_token, log_path="D:\\bhave\\Desktop")
    interval = trade_time-now
    print(f"Code run after {interval.total_seconds()} sec")
    sleep(interval.total_seconds()) if interval.total_seconds() > 0 else sleep(0)
    checkSignal()
