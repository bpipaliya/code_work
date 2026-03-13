from time import sleep, time
from Trading_Setup import credentials
from datetime import datetime, timedelta
import pandas as pd
import talib
import telegram_send
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

SYMBOL_LIST = credentials.N50_LIST
TRADED_SYMBOL = []
TimeFrame = 5


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
    df['ATR'] = talib.ATR(df.high, df.low, df.close, timeperiod=14)
    df['UP_TREND'] = df['DOWN_TREND'] = 0
    for i in range(14, len(df)):
        if df['open'][i] == df['low'][i]:
            df['UP_TREND'].at[i] = 1
        if df['open'][i] == df['high'][i]:
            df['DOWN_TREND'].at[i] = 1

    print(df.tail(2))
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
    start = time()
    global TRADED_SYMBOL

    for symbol in SYMBOL_LIST:
        if symbol not in TRADED_SYMBOL:
            print(symbol)
            candle_df = getHistoricalData(symbol)
            if candle_df is not None:
                latest_candle = candle_df.iloc[-1]
                if latest_candle['UP_TREND'] == 1 and (latest_candle['high']-latest_candle['low']) < 0.01*latest_candle['close']:
                    Side = 1
                    ltp = latest_candle['close']
                    StopPrice = round(latest_candle['high'], 1)
                    LimitPrice = round(StopPrice + 0.05, 2)
                    SL = round(2 * latest_candle['ATR'], 1)
                    Target = round(3 * latest_candle['ATR'], 1)
                    Qty = round(50000 / ltp)

                    # place_order(symbol, qty=Qty, side=Side, stopLoss=SL, takeProfit=Target, stopPrice=StopPrice, limitPrice=LimitPrice)
                    telegram_send.send(messages=[f"OHL Trading\nBuy:\n{symbol}\nEntry Price: {LimitPrice}\nSL: {SL}\nTGT: {Target}\nQTY: {Qty}\n{datetime.now()}"])
                    print(f'Buy {symbol} Stop Price:{StopPrice}  SL:{SL}  TGT:{Target} QTY:{Qty} at {datetime.now()}')
                    TRADED_SYMBOL.append(symbol)

                if latest_candle['DOWN_TREND'] == 1 and (latest_candle['high']-latest_candle['low']) < 0.01*latest_candle['close']:
                    Side = -1
                    ltp = latest_candle['close']
                    StopPrice = round(latest_candle['low'], 1)
                    LimitPrice = round(StopPrice - 0.05, 2)
                    SL = round(2 * latest_candle['ATR'], 1)
                    Target = round(3 * latest_candle['ATR'], 1)
                    Qty = round(50000 / ltp)

                    # place_order(symbol, qty=Qty, side=Side, stopLoss=SL, takeProfit=Target, stopPrice=StopPrice, limitPrice=LimitPrice)
                    telegram_send.send(messages=[f"OHL Trading\nSell:\n{symbol}\nEntry Price: {LimitPrice}\nSL: {SL}\nTGT: {Target}\nQTY: {Qty}\n{datetime.now()}"])
                    print(f'Sell {symbol} Stop Price:{StopPrice}  SL:{SL}  TGT:{Target} QTY:{Qty} at {datetime.now()}')
                    TRADED_SYMBOL.append(symbol)


if __name__ == '__main__':
    fyers = fyersModel.FyersModel(client_id=app_id, token=access_token, log_path="E:\\bhave\\Desktop")
    startTime = datetime.strptime("2021-09-20 9:15:0", "%Y-%m-%d %H:%M:%S")
    interval = startTime - datetime.now()
    print(f"Code run after {interval.total_seconds() if interval.total_seconds() > 0 else sleep(0)} sec")
    sleep(interval.total_seconds()) if interval.total_seconds() > 0 else sleep(0)
    checkSignal()
