from time import sleep

import credentials
from datetime import datetime, timedelta
import pandas as pd
import talib as ta
import pandas_ta as pdta
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
SYMBOL_LIST = credentials.N50_LIST

TRADED_SYMBOL = []
TimeFrame = 5
StartTime = datetime.strptime("2021-09-30 9:25:0", "%Y-%m-%d %H:%M:%S")


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
    df['ATR_14'] = ta.ATR(df.high, df.low, df.close, timeperiod=20)
    df["MACD"], df["MACD_S"], df["MACD_H"] = ta.MACD(df.close, fastperiod=12, slowperiod=26, signalperiod=9)
    df['CMF_20'] = pdta.cmf(df.high, df.low, df.close, df.volume, open_=None, lenght=None, offset=None)
    df['Buy'] = df['Sell'] = 0
    df = df.round(decimals=2)

    for i in range(30, len(df)):
        if 0.1 < df['CMF_20'][i-1] < df['CMF_20'][i] and 0 < df['MACD_H'][i]: # and df['high'][i-1] < df['high'][i]:
            df['Buy'].at[i] = 1
        if -0.1 > df['CMF_20'][i-1] > df['CMF_20'][i] and 0 > df['MACD_H'][i]: # and df['low'][i-1] > df['low'][i]:
            df['Sell'].at[i] = 1

    # print(df.tail(2)
    return df


def getHistoricalData(symbol=SYMBOL_LIST, resolution=TimeFrame):
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

    for symbol in SYMBOL_LIST:
        # print(symbol)
        candle_df = getHistoricalData(symbol)
        if candle_df is not None:
            prev_candle = candle_df.iloc[-2]
            latest_candle = candle_df.iloc[-1]
            if latest_candle['Buy'] == 1 and (max(latest_candle['high'], prev_candle['high']) - min(latest_candle['low'], prev_candle['low'])) < 0.01*latest_candle['close']:
                Side = 1
                ltp = latest_candle['close']
                StopPrice = round(latest_candle['high'], 1)
                LimitPrice = round(StopPrice+0.05, 2)
                SL = round(0.5 * latest_candle [ 'close' ], 1)
                Target = round(0.8 * latest_candle [ 'close' ], 1)
                Qty = round(50000/ltp)

                place_order(symbol, qty=Qty, side=Side, stopLoss=SL, limitPrice=LimitPrice, takeProfit=Target, stopPrice=StopPrice)
                # telegram_send.send(messages=[f"CMF MACD Trading\nBuy:\n{symbol}\nEntry Price: {LimitPrice}\nSL: {SL}\nTGT: {Target}\nQTY: {Qty}\n{datetime.now()}"])
                print(f'Buy {symbol} Stop Price:{StopPrice} limitPrice:{LimitPrice}  SL:{SL}  TGT:{Target} QTY:{Qty} at {datetime.now()}')

            if latest_candle['Sell'] == 1 and (max(latest_candle['high'], prev_candle['high']) - min(latest_candle['low'], prev_candle['low'])) < 0.01*latest_candle['close']:
                Side = -1
                ltp = latest_candle['close']
                StopPrice = round(latest_candle['low'], 1)
                LimitPrice = round(StopPrice-0.05, 2)
                SL = round(0.5*latest_candle['close'], 1)
                Target = round(0.8*latest_candle['close'], 1)
                Qty = round(50000/ltp)

                place_order(symbol, qty=Qty, side=Side, stopLoss=SL,limitPrice=LimitPrice, takeProfit=Target, stopPrice=StopPrice)
                # telegram_send.send(messages=[f"CMF MACD Trading\nSell:\n{symbol}\nEntry Price: {LimitPrice}\nSL: {SL}\nTGT: {Target}\nQTY: {Qty}\n{datetime.now()}"])
                print(f'Sell {symbol} Stop Price:{StopPrice} limitPrice:{LimitPrice} SL:{SL}  TGT:{Target} QTY:{Qty} at {datetime.now()}')


if __name__ == '__main__':
    fyers = fyersModel.FyersModel(client_id=app_id, token=access_token, log_path="E:\\bhave\\Desktop")
    interval = StartTime - datetime.now()
    print(f"Code run after {interval.total_seconds() if interval.total_seconds() > 0 else sleep(0)} sec")
    sleep(interval.total_seconds()) if interval.total_seconds() > 0 else sleep(0)
    checkSignal()
