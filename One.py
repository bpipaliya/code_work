from time import sleep

import credentials
from datetime import datetime, timedelta
import pandas as pd
import talib
import pandas_ta as ta
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
access_token = open("Trading_Setup/access_token_BBP.txt", "r").read()

SYMBOL_LIST = ['NSE:ADANIPORTS-EQ', 'NSE:ASIANPAINT-EQ', 'NSE:AXISBANK-EQ', 'NSE:BAJAJ-AUTO-EQ', 'NSE:BAJAJFINSV-EQ', 'NSE:BAJFINANCE-EQ',
               'NSE:BHARTIARTL-EQ', 'NSE:BPCL-EQ', 'NSE:BRITANNIA-EQ', 'NSE:CIPLA-EQ', 'NSE:COALINDIA-EQ',
               'NSE:DIVISLAB-EQ', 'NSE:DRREDDY-EQ', 'NSE:EICHERMOT-EQ', 'NSE:GRASIM-EQ', 'NSE:HCLTECH-EQ',
               'NSE:HDFCBANK-EQ', 'NSE:HDFC-EQ', 'NSE:HDFCLIFE-EQ', 'NSE:HEROMOTOCO-EQ', 'NSE:HINDALCO-EQ',
               'NSE:HINDUNILVR-EQ', 'NSE:ICICIBANK-EQ', 'NSE:INDUSINDBK-EQ', 'NSE:INFY-EQ', 'NSE:IOC-EQ', 'NSE:ITC-EQ',
               'NSE:JSWSTEEL-EQ', 'NSE:KOTAKBANK-EQ', 'NSE:LT-EQ', 'NSE:M&M-EQ', 'NSE:MARUTI-EQ', 'NSE:NESTLEIND-EQ',
               'NSE:NTPC-EQ', 'NSE:ONGC-EQ', 'NSE:POWERGRID-EQ', 'NSE:RELIANCE-EQ', 'NSE:SBILIFE-EQ', 'NSE:SBIN-EQ',
               'NSE:SHREECEM-EQ', 'NSE:SUNPHARMA-EQ', 'NSE:TATACONSUM-EQ', 'NSE:TATAMOTORS-EQ', 'NSE:TATASTEEL-EQ',
               'NSE:TCS-EQ', 'NSE:TECHM-EQ', 'NSE:TITAN-EQ', 'NSE:ULTRACEMCO-EQ', 'NSE:UPL-EQ', 'NSE:WIPRO-EQ']
TRADED_SYMBOL = []
TimeFrame = 5


async def place_order(symbol, qty, side, stopPrice, limitPrice, stopLoss, takeProfit):
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


async def checkSignal(symbol=SYMBOL_LIST, resolution=TimeFrame):
    # start = time()
    global TRADED_SYMBOL

    for symbol in SYMBOL_LIST:
        if symbol not in TRADED_SYMBOL:
            print(symbol)
            from_date = datetime.now() - timedelta(days=10)
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
            columns = [ 'timestamp', 'open', 'high', 'low', 'close', 'volume' ]
            df = pd.DataFrame(candle_json [ 'candles' ], columns=columns)
            df [ 'timestamp' ] = (
                pd.to_datetime(df [ 'timestamp' ], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
            df [ 'date' ] = pd.to_datetime(df [ 'timestamp' ]).dt.date
            df [ 'time' ] = pd.to_datetime(df [ 'timestamp' ]).dt.strftime('%H:%M')
            df = df [ [ 'date', 'time', 'timestamp', 'open', 'high', 'low', 'close', 'volume' ] ]
            df.drop('timestamp', axis=1, inplace=True)
            df [ 'ATR' ] = talib.ATR(df.high, df.low, df.close, timeperiod=14)
            df [ "MACD" ], df [ "MACD_S" ], df [ "MACD_H" ] = talib.MACD(df.close, fastperiod=12, slowperiod=26,
                                                                         signalperiod=9)
            df [ 'CMF' ] = ta.cmf(df.high, df.low, df.close, df.volume, open_=None, lenght=None, offset=None)
            df [ 'CROSS_UP' ] = df [ 'CROSS_DOWN' ] = df [ 'UP_TREND' ] = df [ 'DOWN_TREND' ] = 0
            df = df.round(decimals=2)

            for i in range(30, len(df)):
                if 0 < df [ 'CMF' ] [ i - 1 ] < df [ 'CMF' ] [ i ] and df [ 'MACD_H' ] [ i - 1 ] < df [ 'MACD_H' ] [
                    i ]:
                    df [ 'CROSS_UP' ].at [ i ] = 1
                if 0 > df [ 'CMF' ] [ i - 1 ] > df [ 'CMF' ] [ i ] and df [ 'MACD_H' ] [ i - 1 ] > df [ 'MACD_H' ] [
                    i ]:
                    df [ 'CROSS_DOWN' ].at [ i ] = 1
                if df [ 'open' ] [ i ] < df [ 'close' ] [ i ]:
                    df [ 'UP_TREND' ].at [ i ] = 1
                if df [ 'open' ] [ i ] > df [ 'close' ] [ i ]:
                    df [ 'DOWN_TREND' ].at [ i ] = 1
            if df is not None:
                prev_candle = df.iloc[-2]
                latest_candle = df.iloc[-1]
                if prev_candle['CROSS_UP'] == 1 and prev_candle['UP_TREND'] == 1 and latest_candle['CROSS_UP'] == 1 and latest_candle['UP_TREND'] == 1 and (max(latest_candle['high'], prev_candle['high']) - min(latest_candle['low'], prev_candle['low'])) < 0.01*latest_candle['close']:
                    Side = 1
                    ltp = latest_candle['close']
                    StopPrice = round(latest_candle['high'], 1)
                    LimitPrice = round(StopPrice+0.05, 2)
                    SL = round(2*latest_candle['ATR'], 1)
                    Target = round(3*latest_candle['ATR'], 1)
                    Qty = round(50000/ltp)

                    # place_order(symbol, qty=Qty, side=Side, stopLoss=SL, limitPrice=LimitPrice, takeProfit=Target, stopPrice=StopPrice)
                    # telegram_send.send(messages=[f"CMF MACD Trading\nBuy:\n{symbol}\nEntry Price: {LimitPrice}\nSL: {SL}\nTGT: {Target}\nQTY: {Qty}\n{datetime.now()}"])
                    print(f'Buy {symbol} Stop Price:{StopPrice} limitPrice:{LimitPrice}  SL:{SL}  TGT:{Target} QTY:{Qty} at {datetime.now()}')
                    TRADED_SYMBOL.append(symbol)

                if prev_candle['CROSS_DOWN'] == 1 and prev_candle['DOWN_TREND'] == 1 and latest_candle['CROSS_DOWN'] == 1 and latest_candle['DOWN_TREND'] == 1 and (max(latest_candle['high'], prev_candle['high']) - min(latest_candle['low'], prev_candle['low'])) < 0.01*latest_candle['close']:
                    Side = -1
                    ltp = latest_candle['close']
                    StopPrice = round(latest_candle['low'], 1)
                    LimitPrice = round(StopPrice-0.05, 2)
                    SL = round(2*latest_candle['ATR'], 1)
                    Target = round(3*latest_candle['ATR'], 1)
                    Qty = round(50000/ltp)

                    # place_order(symbol, qty=Qty, side=Side, stopLoss=SL, limitPrice=LimitPrice, takeProfit=Target, stopPrice=StopPrice)
                    # telegram_send.send(messages=[f"CMF MACD Trading\nSell:\n{symbol}\nEntry Price: {LimitPrice}\nSL: {SL}\nTGT: {Target}\nQTY: {Qty}\n{datetime.now()}"])
                    print(f'Sell {symbol} Stop Price:{StopPrice} limitPrice:{LimitPrice} SL:{SL}  TGT:{Target} QTY:{Qty} at {datetime.now()}')
                    TRADED_SYMBOL.append(symbol)

    # interval = timeFrame - (time()-start)
    # print(interval)
    # threading.Timer(interval, checkSignal).start()


if __name__ == '__main__':
    fyers = fyersModel.FyersModel(client_id=app_id, token=access_token, log_path="E:\\bhave\\Desktop")

    startTime = datetime.strptime("2021-09-15 9:25:0", "%Y-%m-%d %H:%M:%S")
    interval = startTime - datetime.now()
    print(f"Code run after {interval.total_seconds() if interval.total_seconds() > 0 else sleep(0)} sec")
    sleep(interval.total_seconds()) if interval.total_seconds() > 0 else sleep(0)
    checkSignal()
    # interval = timeFrame - datetime.now().second
    # print(f"Code run after {interval} sec")
    # sleep(interval)
    # checkSignal()
