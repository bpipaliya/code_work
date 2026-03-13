from time import sleep, time
import credentials
from datetime import datetime, timedelta
import pandas as pd
import talib as ta
import pandas_ta as pdta
import threading
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
timeFrame = 300


def calculate_indicator(res_json):
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df = pd.DataFrame(res_json['candles'], columns=columns)
    df['timestamp'] = (pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    df['time'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M')
    df = df[['date', 'time', 'timestamp', 'open', 'high', 'low', 'close', 'volume']]
    df.drop('timestamp', axis=1, inplace=True)
    df [ 'ATR_14' ] = ta.ATR(df.high, df.low, df.close, timeperiod=20)
    df["MACD"], df["MACD_S"], df["MACD_H"] = ta.MACD(df.close, fastperiod=12, slowperiod=26, signalperiod=9)
    df['CMF'] = pdta.cmf(df.high, df.low, df.close, df.volume)
    df [ 'ST' ] = pdta.supertrend(high=df.high, low=df.low, close=df.close, period=7, multiplier=3) [ 'SUPERT_7_3.0' ]
    df['Buy'] = df['Sell'] = 0
    df = df.round(decimals=2)

    for i in range(30, len(df)):
        if df['RSI_14'][i] > 60 and df['CMF'][i] > 0.02 and df['MACD_H'][i] > 0 and df['close'] > df['ST']:  # and df['ARRON_U'][i] > 50 and df['AROON_D'][i] < 50:
            df['RSI_14_UP'].at[i] = 1
        if df['RSI_14'][i] < 40 < df['RSI_14'][i - 1] or df['RSI_14'][i] < 60 < df['RSI_14'][i - 1] and df['DMP_14'][i] < df['DMN_14'][i]:  # and df['ARRON_U'][i] < 50 and df['AROON_D'][i] > 50:
            df['RSI_14_DOWN'].at[i] = 1
    # print(df.tail(2))
    return df


def getHistoricalData(symbol=SYMBOL_LIST, resolution=5):
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
    return calculate_indicator(candle_json)


def checkSignal():
    start = time()
    global TRADED_SYMBOL

    for symbol in SYMBOL_LIST:
        # if symbol not in TRADED_SYMBOL:
        # print(symbol)
        candel_df = getHistoricalData(symbol)
        if candel_df is not None:
            previ_candel = candel_df.iloc[-2]
            latest_candel = candel_df.iloc[-1]

            if latest_candel['RSI_14_UP'] == 1:
                ltp = latest_candel['close']
                StopPrice = latest_candel['high']
                SL = round(2 * latest_candel['ATR'], 1)
                Target = round(4 * latest_candel['ATR'], 1)
                Qty = round(50000 / ltp, 0)

                # telegram_send.send(messages=[
                #     f"RSI_BOT\nBuy:\n{symbol}\nEntry Price: {StopPrice}\nSL: {SL}\nTGT: {Target}\nQTY: {Qty}\nPREVI_RSI= {previ_candel['RSI_14']}\nRSI= {latest_candel['RSI_14']}\n{datetime.now().time()}"])
                print(f'Buy Order Placed for {symbol} Stop Price {StopPrice}  SL {SL}  TGT {Target} QTY {Qty} at{datetime.now()}')
                # TRADED_SYMBOL.append(symbol)

            if latest_candel['RSI_14_DOWN'] == 1:
                ltp = latest_candel['close']
                StopPrice = latest_candel['low']
                SL = round(2 * latest_candel['ATR'], 1)
                Target = round(4 * latest_candel['ATR'], 1)
                Qty = round(50000 / ltp, 0)

                # telegram_send.send(messages=[
                #     f"RSI_BOT\nSell:\n{symbol}\nEntry Price: {StopPrice}\nSL: {SL}\nTGT: {Target}\nQTY: {Qty}\nPREVI_RSI= {previ_candel['RSI_14']}\nRSI= {latest_candel['RSI_14']}\n{datetime.now().time()}"])
                print(f'Sell Order Placed for {symbol} Stop Price {StopPrice}  SL {SL}  TGT {Target} QTY {Qty} at{datetime.now()}')
                # TRADED_SYMBOL.append(symbol)

    interval = timeFrame - (time() - start)
    print(time())
    print(interval)
    threading.Timer(interval, checkSignal).start()


if __name__ == '__main__':
    fyers = fyersModel.FyersModel(client_id=app_id, token=access_token, log_path="D:\\Google Drive\\Bhavesh_Data\\Trading_Stratery\\Fyers\\log_file")
    startTime = datetime.strptime("2021-09-13 12:0:0", "%Y-%m-%d %H:%M:%S")
    interval = startTime - datetime.now()
    print(f"Code run after {interval.total_seconds() if interval.total_seconds() > 0 else sleep(0)} sec")
    sleep(interval.total_seconds()) if interval.total_seconds() > 0 else sleep(0)
    checkSignal()

