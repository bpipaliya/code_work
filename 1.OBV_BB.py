##pip install numpy==1.26.4
##pip install setuptools
import fy_lib
import os
import talib as ta
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

traded_symbol = []

def checkSignal():
    while datetime.now().time() < time(23, 30):
        try:
            fy_lib.read_file()
        except FileNotFoundError:
            print('File Not Found, Getting the access token!')
            fy_lib.get_access_token()
            fyers = fyersModel.FyersModel(client_id=fy_lib.fyers_api_id_BBP, is_async=False, token=fy_lib.read_file, log_path=os.getcwd())
            response = fyers.get_profile()
            if 'error' in response['s'] or 'error' in response['message'] or 'expired' in response['message']:
                print(response)
                print('Getting a access token!')
                fy_lib.get_access_token()
            else:
                print('You already have a access token!')
                print(response)
        finally:
            fyers = fyersModel.FyersModel(client_id=fy_lib.fyers_api_id_BBP, is_async=False, token=fy_lib.read_file, log_path=os.getcwd())       
            for symbol in fy_lib.N50_LIST:
                print(symbol)
                from_date = (datetime.now()-timedelta(days=4)).strftime("%Y-%m-%d")
                to_date = (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d")
                data = {
                    "symbol": symbol,
                    "resolution": 5,
                    "date_format": 1,
                    "range_from": from_date,
                    "range_to": to_date,
                    "cont_flag": 0
                }
                df = fyers.history(data)
                columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                df = pd.DataFrame(df['candles'], columns=columns)
                df['timestamp'] = (pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
                df["symbol"] = symbol
                df.set_index(pd.DatetimeIndex(df["timestamp"]), inplace=True)
                df['date'] = pd.to_datetime(df['timestamp']).dt.date
                df['time'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M')
                df.drop('timestamp', axis=1, inplace=True)
                df["OBV"] = pdta.obv(df.close, df.volume)
                df["BBU"], df["BBM"], df["BBL"] = ta.BBANDS(df["OBV"], timeperiod=20, nbdevup=2, nbdevdn=2)
                df["BBU"] = pdta.bbands(df["OBV"], length=22, std=2)["BBU_22_2.0"]
                df["BBL"] = pdta.bbands(df["OBV"], length=22, std=2)["BBL_22_2.0"]
                df['Buy'] = df['Sell'] = 0
                df = df.round(decimals=2)
                if df is not None:
                    pt = pd.Timestamp.now(tz='Asia/Kolkata').replace(hour=9, minute=15, second=0,
                                                                                            microsecond=0)
                    lt = pd.Timestamp.now(tz='Asia/Kolkata').replace(hour=9, minute=20, second=0,
                                                                                            microsecond=0)
                    prev_candle = df.loc[pt]
                    latest_candle = df.loc[lt]

                    if prev_candle['OBV'] > prev_candle["BBU"] and latest_candle['OBV'] > latest_candle["BBU"] and latest_candle["close"] > prev_candle["high"]:
                        traded_symbol.append(symbol)
                        # HighPrice = round(latest_candle['high'], 1)
                        # obv = latest_candle.OBV
                        # bbu = latest_candle.BBU
                        # telegram_send.send(messages=[f"CMF MACD Trading\nBuy:\n{symbol}\nEntry Price: {LimitPrice}\nSL: {SL}\nTGT: {Target}\nQTY: {Qty}\n{datetime.now()}"])
                        # print(
                        #     f'Buy {symbol} above Price:{HighPrice} obv={obv} bbu={bbu}at {datetime.now()}')

                    if prev_candle['OBV'] < prev_candle["BBL"] and latest_candle['OBV'] < latest_candle["BBL"] and latest_candle["close"] < prev_candle["low"]:
                        traded_symbol.append(symbol)

                    #     LowPrice = round(latest_candle['high'], 1)
                    #     obv = latest_candle.OBV
                    #     bbl = latest_candle.BBL
                    #     # telegram_send.send(messages=[f"CMF MACD Trading\nSell:\n{symbol}\nEntry Price: {LimitPrice}\nSL: {SL}\nTGT: {Target}\nQTY: {Qty}\n{datetime.now()}"])
                    #     print(
                    #         f'Sell {symbol} below Price:{LowPrice} obv={obv} bbu={bbl} at {datetime.now()}')
            df = pd.DataFrame(traded_symbol)
            print(df)
            df.to_csv(os.getcwd() + "\\2.txt", mode='a', header=True, index=True)
            print(f"last update at {datetime.now()}")
            sleep(TimeFrame*60)


if __name__ == '__main__':
    interval = StartTime - datetime.now()
    print(f"Code run after {interval.total_seconds() if interval.total_seconds() > 0 else sleep(0)} sec")
    sleep(interval.total_seconds()) if interval.total_seconds() > 0 else sleep(0)
    checkSignal()
