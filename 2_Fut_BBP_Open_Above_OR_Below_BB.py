from time import sleep
import fy_lib
from datetime import datetime, timedelta
import pandas as pd
import pandas_ta as pdta
import talib as ta
import telegram_send
from fyers_api import fyersModel

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

app_id = fyers_lib.fyers_api2_id_BBP
app_secret = fyers_lib.fyers_api2_secret_BBP
redirect_url = fyers_lib.fyers_redirect_url
password = fyers_lib.fyers_pwd_BBP
two_fa = fyers_lib.fyers_two_fa_BBP
user_id = fyers_lib.fyers_user_id_BBP
access_token = open("access_token2_BBP.txt", "r").read()
TimeFrame = 5
now = pd.Timestamp.now(tz='Asia/Kolkata')
trade_time = now.replace(hour=9, minute=20, second=0, microsecond=0)
# StartTime = datetime.strptime("2021-10-12 9:20:0", "%Y-%m-%d %H:%M:%S")

SYMBOL_LIST = [name[:-3] + '21NOVFUT' for name in fyers_lib.N50_LIST]


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
    df['BBU'], df['BBM'], df['BBL'] = ta.BBANDS(df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df['CMF_20'] = pdta.cmf(df.high, df.low, df.close, df.volume, open_=None, lenght=None, offset=None)
    df['ATR_14'] = ta.ATR(df.high, df.low, df.close, timeperiod=14)
    df['Buy'] = df['Sell'] = 0
    df = df.round(decimals=2)

    for i in range(30, len(df)):
        if df['open'][i] > df['BBU'][i] and df['close'][i] > df['BBM'][i] and df['CMF_20'][i] < 0 and df['open'][i] > df['close'][i]:
            df['Sell'].at[i] = 1
        if df['open'][i] < df['BBL'][i] and df['close'][i] < df['BBM'][i] and df['CMF_20'][i] > 0 and df['open'][i] < df['close'][i]:
            df['Buy'].at[i] = 1
    print(df.tail(5))
    return df


def getHistoricalData(symbol, resolution=5):
    from_date = datetime.now() - timedelta(days=2)
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
        print(symbol)
        candle_df = getHistoricalData(symbol)
        if candle_df is not None:
            latest_candle = candle_df.iloc[-1]
            if latest_candle['Buy'] == 1 and (latest_candle['high'] - latest_candle['low']) < 0.01*latest_candle['close']:
                Side = 1
                ltp = latest_candle['close']
                StopPrice = round(latest_candle['high'], 1)
                LimitPrice = round(StopPrice + 0.05, 2)
                SL = round(0.005 * latest_candle [ 'high' ], 1)
                Target = round(0.005 * latest_candle [ 'high' ], 1)
                Qty = fyers_lib.N50_FUT_LOTSIZE[symbol]

                place_order(symbol, qty=Qty, side=Side, stopLoss=SL, limitPrice=LimitPrice, takeProfit=Target, stopPrice=StopPrice)
                telegram_send.send(messages=[f"Buy {symbol}\n{datetime.now()}"])
                print(f"Buy {symbol}\n{datetime.now()}")

            if latest_candle['Sell'] == 1 and (latest_candle['high'] - latest_candle['low']) < 0.01*latest_candle['close']:
                Side = -1
                ltp = latest_candle['close']
                StopPrice = round(latest_candle['low'], 1)
                LimitPrice = round(StopPrice - 0.05, 2)
                SL = round(0.005 * latest_candle [ 'low' ], 1)
                Target = round(0.005 * latest_candle [ 'low' ], 1)
                Qty = fyers_lib.N50_FUT_LOTSIZE[symbol]

                place_order(symbol, qty=Qty, side=Side, stopLoss=SL, limitPrice=LimitPrice, takeProfit=Target, stopPrice=StopPrice)
                telegram_send.send(messages=[f"Sell {symbol}\n{datetime.now()}"])
                print(f"Sell {symbol}\n{datetime.now()}")


if __name__ == '__main__':
    fyers = fyersModel.FyersModel(client_id=app_id, token=access_token, log_path="E:\\bhave\\Desktop")
    interval = trade_time - now
    print(f"Code run after {interval.total_seconds() if interval.total_seconds() > 0 else sleep(0)} sec")
    sleep(interval.total_seconds()) if interval.total_seconds() > 0 else sleep(0)
    checkSignal()
