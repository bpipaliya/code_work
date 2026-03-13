from smartapi import SmartConnect
import pandas as pd
import pandas_ta as pdta
from datetime import datetime, timedelta
import credentials
from time import time, sleep
import talib as ta
import threading
import warnings
import telegram_send
from fyers_api import fyersModel
from fy_lib import *
warnings.filterwarnings('ignore')
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)


SYMBOL_LIST = ['ADANIPORTS', 'AXISBANK', 'BAJAJ-AUTO', 'BAJAJFINSV', 'BAJFINANCE', 'BHARTIARTL', 'BPCL',
               'BRITANNIA', 'CIPLA', 'COALINDIA', 'DIVISLAB', 'DRREDDY', 'EICHERMOT', 'GRASIM', 'HCLTECH', 'HDFCBANK',
               'HDFC', 'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDUNILVR', 'ICICIBANK', 'INDUSINDBK', 'INFY', 'IOC',
               'ITC', 'JSWSTEEL', 'KOTAKBANK', 'LT', 'M&M', 'MARUTI', 'NESTLEIND', 'NTPC', 'ONGC', 'POWERGRID',
               'RELIANCE', 'SBILIFE', 'SBIN', 'SHREECEM', 'SUNPHARMA', 'TATACONSUM', 'TATAMOTORS', 'TATASTEEL', 'TCS',
               'TECHM', 'TITAN', 'ULTRACEMCO', 'UPL', 'WIPRO']
TRADED_SYMBOL = []
timeFrame = 900 + 5  # 5 sec coz dealy repsone of historical API
now = pd.Timestamp.now(tz='Asia/Kolkata')
trade_time = now.replace(hour=13, minute=45, second=0, microsecond=0)
access_token = open("access_token2_BBP.txt", "r").read()


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


def intializeSymbolTokenMap():
    # url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
    # d = requests.get(url).json()
    global token_df
    token_df = pd.read_csv("G:/My Drive/Trading_Stratery/Fyers/angle_token.csv")
    # token_df = token_df[(token_df['expiry'] == "2021-10-28") ]
    # token_df = pd.DataFrame.from_dict(d)
    # token_df['expiry'] = pd.to_datetime(token_df['expiry'])
    # token_df = token_df.astype({'strike': float})
    TOKEN_MAP = token_df


def getTokenInfo(symbol, exch_seg='NFO', instrumenttype='FUTSTK',strike_price='', pe_ce=''):
    df = TOKEN_MAP
    strike_price = strike_price*100
    if exch_seg == 'NSE':
        eq_df = df[(df['exch_seg'] == 'NSE') & (df['symbol'].str.contains('EQ'))]
        return eq_df[eq_df['name'] == symbol]
    elif exch_seg == 'NFO' and ((instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX')):
        return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol)].sort_values(by=['expiry'])
    elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
        return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) &
                  (df['strike'] == strike_price) & (df['symbol'].str.endswith(pe_ce))].sort_values(by=['expiry'])


def calculate_indicator(res_json):
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df = pd.DataFrame(res_json['data'], columns=columns)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%dT%H:%M:%S')
    df['RSI'] = ta.RSI(df.close, timeperiod=14)
    df["RSMA_20"] = ta.MA(df['RSI'], timeperiod=20)
    df['CMF'] = pdta.cmf(df.high, df.low, df.close, df.volume, open_=None, lenght=None, offset=None)
    df["CSMA_20"] = ta.MA(df['CMF'], timeperiod=20)
    df [ "SMA_9" ] = ta.MA(df [ 'close' ], timeperiod=9)
    df["volatility"] = round((df["high"]-df["low"])*100/df["open"],2)
    df['BUY'] = df['SELL'] = 0
    df = df.round(decimals=2)
    
    for i in range(20, len(df)):
        if df['RSI'][i-1] <= df["RSMA_20"][i-1] and df['RSI'][i] > df["RSMA_20"][i] and df['CMF'][i] >  df["CSMA_20"][i]:
            df['BUY'][i] = 1
        if df['RSI'][i-1] >= df["RSMA_20"][i-1] and df['RSI'][i] < df["RSMA_20"][i] and df['CMF'][i] <  df["CSMA_20"][i]:
            df['SELL'][i] = 1

    # print(df.tail(10))
    return df


def getHistoricalAPI(token, interval='FIFTEEN_MINUTE'):
    to_date = datetime.now() + timedelta(days=1)
    from_date = to_date - timedelta(days=6)
    from_date_format = from_date.strftime("%Y-%m-%d %H:%M")
    to_date_format = to_date.strftime("%Y-%m-%d %H:%M")
    try:
        historicParam = {
            "exchange": "NFO",
            "symboltoken": token,
            "interval": interval,
            "fromdate": from_date_format,
            "todate": to_date_format
        }
        candle_json = SMART_API_OBJ.getCandleData(historicParam)
        return calculate_indicator(candle_json)
    except Exception as e:
        print("Historic Api failed: {}".format(e))


def checkSingnal():
    while time(9, 15) <= pd.Timestamp.now(tz='Asia/Kolkata').time() <= time(23, 15):
        timenow = pd.Timestamp.now(tz='Asia/Kolkata')
        check = True if int(timenow.minute) / TimeFrame in list(np.arange(0.0, 4.0)) else False
        if check:
            nextscan = timenow+timedelta(minutes=TimeFrame)
            for symbol in SYMBOL_LIST:
                print(symbol)
                lt = (pd.Timestamp.now(tz='Asia/Kolkata')-timedelta(minutes=15)).replace(second=0, microsecond=0)
                pt = (pd.Timestamp.now(tz='Asia/Kolkata')-timedelta(minutes=30)).replace(second=0, microsecond=0)
                candle_df = historicalData(symbol)
                if candle_df is not None:
                    prev_candle = candle_df.loc[pt]
                    latest_candle = candle_df.loc[lt]

                    if prev_candle['O_DOWN'] == 1 and latest_candle['O_BUY'] == 1:
                        telegram_send.send(messages=[f"OBV.Cross-BUY {symbol}\n{datetime.now()}"])
                        print(f"OBV-Buy {symbol}\n{datetime.now()}")

                    if prev_candle['O_UP'] == 1 and latest_candle['O_SELL'] == 1:
                        telegram_send.send(messages=[f"OBV.Cross-SELL {symbol}\n{datetime.now()}"])
                        print(f"OBV-Sell {symbol}\n{datetime.now()}")


            waitsecs = int((nextscan-pd.Timestamp.now(tz='Asia/Kolkata')).seconds)
            print(f"Next Scan {nextscan.replace(second=0, microsecond=0)}")
            sleep(waitsecs) if waitsecs > 0 else sleep(0)


if __name__ == '__main__':
    fyers = fyersModel.FyersModel(client_id=fyers_api2_id_BBP, token=access_token, log_path="D:\\bhave\\Desktop")
    intializeSymbolTokenMap()
    obj = SmartConnect(api_key=angle_api_key)
    data = obj.generateSession(angle_username, angle_password)
    SMART_API_OBJ = obj
   
    interval = trade_time - now
    print(f"Code run after {interval.total_seconds()} sec")
    sleep(interval.total_seconds()) if interval.total_seconds() > 0 else sleep(0)
    checkSingnal()

   
