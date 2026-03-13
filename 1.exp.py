import os
import warnings
from datetime import datetime, timedelta, time
import pandas as pd
import pandas_ta as pdta
from fyers_apiv3 import fyersModel
from fy_lib import * 
import talib as ta
pd.set_option('display.max_columns', None)
warnings.filterwarnings('ignore')
symbol_list= ["NSE:ADANIPORTS-EQ"] #fy_lib.N50_LIST #
# for symbol in symbol_list:
#     df=fy_lib.historical_data(symbol, delta=4,resolution=5)
#     df["symbol"] = symbol
#     df.set_index(pd.DatetimeIndex(df["timestamp"]), inplace=True)
#     # print(df.tail(5))
#     # df['timestamp'] = (pd.to_datetime(df['timestamp'],
#     #                                  format='%Y-%m-%dT%H:%M:%S').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))

#     df['date'] = pd.to_datetime(df['timestamp']).dt.date
#     df['time'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M')
#     # df = df[['date', 'time', 'timestamp', 'open', 'high', 'low', 'close', 'volume']]
#     df.drop('timestamp', axis=1, inplace=True)
#     df["OBV"] = pdta.obv(df.close, df.volume)
#     # df["BBU"], df["BBM"], df["BBL"] = ta.BBANDS(df["OBV"], timeperiod=20, nbdevup=2, nbdevdn=2)
#     # print(df)
#     # lt = pd.Timestamp.now(tz='Asia/Kolkata').replace(hour=9,minute= 15,second=0, microsecond=0).time
#     # pt = pd.Timestamp.now(tz='Asia/Kolkata').replace(hour=9, minute=20,second=0, microsecond=0).time
#     lt = time(hour=9, minute=20)
#     pt = time(hour=9, minute=15)
#     # print(lt)
#     # print(pt)
#     prev_candle = df.loc[pt]
#     latest_candle = df.loc[lt]
#     if latest_candle["OBV"] > prev_candle["OBV"]:
#         print(symbol)
#     # print(prev_candle)
#     # print(latest_candle)

try:
    fyers = fyersModel.FyersModel(client_id=fyers_api_id_BBP, is_async=False, token=read_file, log_path=os.getcwd())
    from_date = (datetime.now()-timedelta(days=4)).strftime("%Y-%m-%d")
    to_date = (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d")
    data = {
        "symbol": symbol_list,
        "resolution": 5,
        "date_format": 1,
        "range_from": from_date,
        "range_to": to_date,
        "cont_flag": 0
    }
    df = fyers.history(data)
    print(df)
except'error' in df['s'] or 'error' in df['message'] or 'expired' in df['message']:
    print('Getting a access token!')
    get_access_token()
    
finally:
    fyers = fyersModel.FyersModel(client_id=fyers_api_id_BBP, is_async=False, token=read_file, log_path=os.getcwd())
    from_date = (datetime.now()-timedelta(days=4)).strftime("%Y-%m-%d")
    to_date = (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d")
    data = {
        "symbol": symbol_list,
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
    print(df)