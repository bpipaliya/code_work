import fy_lib
import os
import pandas as pd
import pandas_ta as pdta
import sys
import warnings
from datetime import time, datetime, timedelta
from time import sleep

from fyers_apiv3 import fyersModel

pd.set_option('display.max_columns', None)
warnings.filterwarnings('ignore')
TimeFrame = 5
StartTime = datetime.strptime("2021-09-30 9:20:0", "%Y-%m-%d %H:%M:%S")

SYMBOL_LIST = []


def calculate_indicator(res_json):
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df = pd.DataFrame(res_json['candles'], columns=columns)
    df['timestamp'] = (pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    df['time'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M')
    df = df[['date', 'time', 'timestamp', 'open', 'high', 'low', 'close', 'volume']]
    df.drop('timestamp', axis=1, inplace=True)
    df["obv"] = pdta.obv(df.close, df.volume)
    df["bb"] = pdta.bbands(df["obv"],length=22, std=2)
    df['CMF_20'] = pdta.cmf(df.high, df.low, df.close, df.volume, open_=None, lenght=None, offset=None)
    df['Buy'] = df['Sell'] = 0
    df = df.round(decimals=2)

    for i in range(30, len(df)):
        if ['obv'][i] > df['bb'][i-1] and 0 < df['MACD_H'][i]: # and df['high'][i-1] < df['high'][i]:
            df['Buy'].at[i] = 1
        if ['obv'][i] < df['bb'][i-1] > df['CMF_20'][i] and 0 > df['MACD_H'][i]: # and df['low'][i-1] > df['low'][i]:
            df['Sell'].at[i] = 1

    # print(df.tail(2)
    return df


def getHistoricalData(symbol, resolution=TimeFrame):
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
    while datetime.now().time() < time(23, 30):
        for symbol in SYMBOL_LIST:
            candle_df = getHistoricalData(symbol)
            if candle_df is not None:
                prev_candle = candle_df.iloc[-2]
                latest_candle = candle_df.iloc[-1]
                if latest_candle['Buy'] == 1 and (
                        max(latest_candle['high'], prev_candle['high']) - min(latest_candle['low'],
                                                                              prev_candle['low'])) < 0.01 * \
                        latest_candle['close']:
                    Side = 1
                    ltp = latest_candle['close']
                    StopPrice = round(latest_candle['high'], 1)
                    LimitPrice = round(StopPrice + 0.05, 2)
                    SL = round(0.5 * latest_candle['close'], 1)
                    Target = round(0.8 * latest_candle['close'], 1)
                    Qty = round(50000 / ltp)
                    # telegram_send.send(messages=[f"CMF MACD Trading\nBuy:\n{symbol}\nEntry Price: {LimitPrice}\nSL: {SL}\nTGT: {Target}\nQTY: {Qty}\n{datetime.now()}"])
                    print(
                        f'Buy {symbol} Stop Price:{StopPrice} limitPrice:{LimitPrice}  SL:{SL}  TGT:{Target} QTY:{Qty} at {datetime.now()}')

                if latest_candle['Sell'] == 1 and (
                        max(latest_candle['high'], prev_candle['high']) - min(latest_candle['low'],
                                                                              prev_candle['low'])) < 0.01 * \
                        latest_candle['close']:
                    Side = -1
                    ltp = latest_candle['close']
                    StopPrice = round(latest_candle['low'], 1)
                    LimitPrice = round(StopPrice - 0.05, 2)
                    SL = round(0.5 * latest_candle['close'], 1)
                    Target = round(0.8 * latest_candle['close'], 1)
                    Qty = round(50000 / ltp)

                    # telegram_send.send(messages=[f"CMF MACD Trading\nSell:\n{symbol}\nEntry Price: {LimitPrice}\nSL: {SL}\nTGT: {Target}\nQTY: {Qty}\n{datetime.now()}"])
                    print(
                        f'Sell {symbol} Stop Price:{StopPrice} limitPrice:{LimitPrice} SL:{SL}  TGT:{Target} QTY:{Qty} at {datetime.now()}')
        print(f"last update at {datetime.now()}")
        sleep(fy_lib.RefreshRate)


if __name__ == '__main__':
    try:
        token = fy_lib.read_file()
    except FileNotFoundError:
        print('Getting the access token!')
        fy_lib.get_access_token()
        sys.exit()
    fyers = fyersModel.FyersModel(client_id=fy_lib.fyers_api_id_BBP, is_async=False, token=token, log_path=os.getcwd())
    response = fyers.get_profile()
    if 'error' in response['s'] or 'error' in response['message'] or 'expired' in response['message']:
        print('Getting a access token!')
        fy_lib.get_access_token()
    else:
        print('You already have a access token!')
        print(response)
    interval = StartTime - datetime.now()
    print(f"Code run after {interval.total_seconds() if interval.total_seconds() > 0 else sleep(0)} sec")
    sleep(interval.total_seconds()) if interval.total_seconds() > 0 else sleep(0)
    checkSignal()
