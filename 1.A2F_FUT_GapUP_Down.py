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
timeFrame = 300 + 5  # 5 sec coz dealy repsone of historical API
now = pd.Timestamp.now(tz='Asia/Kolkata')
trade_time = now.replace(hour=15, minute=5, second=0, microsecond=0)
NoTrade = "10:30"
access_token = open("access_token_BBP.txt", "r").read()


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
    # token_df = token_df [ (token_df [ 'expiry' ] == "2021-10-28") ]
    # token_df = pd.DataFrame.from_dict(d)
    # token_df['expiry'] = pd.to_datetime(token_df['expiry'])
    # token_df = token_df.astype({'strike': float})
    credentials.TOKEN_MAP = token_df


def getTokenInfo(symbol, exch_seg='NFO', instrumenttype='FUTSTK', expiry = datetime.strptime("25-11-2021", "%d-%m-%Y"),strike_price='', pe_ce=''):
    df = credentials.TOKEN_MAP
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
    df [ 'BBU' ], df [ 'BBM' ], df [ 'BBL' ] = ta.BBANDS(df [ 'close' ], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df [ 'CMF_20' ] = pdta.cmf(df.high, df.low, df.close, df.volume, open_=None, lenght=None, offset=None)
    df [ 'BUY' ] = df [ 'SELL' ] = 0
    df = df.round(decimals=2)

    for i in range(30, len(df)):
        if df['open'][i]>df['BBU'][i] and df['close'][i]>df['BBM'][i] and df['CMF_20'][i] < 0 and df['close'][i] > df['BBM'][i] and df['open'][i] > df['close'][i]:
            df['SELL'].at[i] = 1
        if df['open'][i] < df['BBL'][i] and df['close'][i] < df['BBM'][i] and df['CMF_20'][i] > 0 and df['close'][i] < df['BBM'][i] and df['open'][i] < df['close'][i]:
            df['BUY'].at[i] = 1

    print(df.tail(2))
    return df


def getHistoricalAPI(token, interval='FIVE_MINUTE'):
    to_date = datetime.now() + timedelta(days=1)
    from_date = to_date - timedelta(days=3)
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
        candle_json = credentials.SMART_API_OBJ.getCandleData(historicParam)
        return calculate_indicator(candle_json)
    except Exception as e:
        print("Historic Api failed: {}".format(e))


def checkSingnal():
    start = time()
    global TRADED_SYMBOL

    for symbol in SYMBOL_LIST:
        tokenInfo = getTokenInfo(symbol).iloc[0]
        token = tokenInfo['token']
        symbol = tokenInfo['symbol']
        print(symbol, token)
        candle_df = getHistoricalAPI(token)
        if candle_df is not None:
            latest_candle = candle_df.iloc[-1]
            if latest_candle['BUY'] == 1 and (latest_candle['high'] - latest_candle['low']) < 0.01 * latest_candle['close']:
                Symbol = credentials.CONVERT_LIST[symbol]
                Side = 1
                ltp = latest_candle [ 'close' ]
                StopPrice = round(latest_candle [ 'high' ], 1)
                LimitPrice = round(StopPrice + 0.05, 2)
                SL = round(0.002 * latest_candle [ 'close' ], 1)
                Target = round(0.005 * latest_candle [ 'close' ], 1)
                Qty = credentials.N50_FUT_LOTSIZE [ Symbol ]

                place_order(symbol=Symbol, qty=Qty, side=Side, stopLoss=SL, limitPrice=LimitPrice, takeProfit=Target,
                            stopPrice=StopPrice)
                telegram_send.send(messages=[ f"BUY {symbol}\n{datetime.now()}" ])
                print(f"BUY {symbol}\n{datetime.now()}")

            if latest_candle['SELL'] == 1 and (latest_candle['high'] - latest_candle['low']) < 0.01 * latest_candle['close']:
                Symbol = credentials.CONVERT_LIST [ symbol ]
                Side = -1
                ltp = latest_candle [ 'close' ]
                StopPrice = round(latest_candle [ 'low' ], 1)
                LimitPrice = round(StopPrice - 0.05, 2)
                SL = round(0.002 * latest_candle [ 'close' ], 1)
                Target = round(0.005 * latest_candle [ 'close' ], 1)
                Qty = credentials.N50_FUT_LOTSIZE [ Symbol ]

                place_order(symbol=Symbol, qty=Qty, side=Side, stopLoss=SL, limitPrice=LimitPrice, takeProfit=Target,
                            stopPrice=StopPrice)
                telegram_send.send(messages=[ f"SELL {symbol}\n{datetime.now()}" ])
                print(f"Sell {symbol}\n{datetime.now()}")


    interval = timeFrame - (time()-start)
    print(interval)
    threading.Timer(interval, checkSingnal).start()


if __name__ == '__main__':
    fyers = fyersModel.FyersModel(client_id=credentials.fyers_api_id_BBP, token=access_token, log_path="E:\\bhave\\Desktop")
    intializeSymbolTokenMap()
    obj = SmartConnect(api_key=credentials.angle_api_key)
    data = obj.generateSession(credentials.angle_username, credentials.angle_password)
    credentials.SMART_API_OBJ = obj
   
    interval = trade_time - now
    print(f"Code run after {interval.total_seconds()} sec")
    sleep(interval.total_seconds()) if interval.total_seconds() > 0 else sleep(0)
    checkSingnal()

   
