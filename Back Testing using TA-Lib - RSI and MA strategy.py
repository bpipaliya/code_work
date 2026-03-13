from pandas.core.indexes.base import Index
import talib as ta
import pandas as pd
import copy
import numpy as np
import pandas_ta as pdta
import fy_lib
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

def symbols_backtesting(symbol_list):
    all_trades = []
    for symbol in symbol_list:
        df = fy_lib.historical_data(symbol, delta=18, resolution=15)
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        df = pd.DataFrame(df['candles'], columns=columns)
        df['timestamp'] = (
            pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        df.set_index(pd.DatetimeIndex(df["timestamp"]), inplace=True)
        df.drop('timestamp', axis=1, inplace=True)
        df['VWAP'] = pdta.vwap(df.high, df.low, df.close, df.volume, anchor=None, offset=None)
        df.reset_index(inplace=True)
        df['RSI'] = ta.RSI(df.close, timeperiod=14)
        df["REMA_9"] = ta.EMA(df['RSI'], timeperiod=9)
        df['OBV'] = ta.OBV(df.close, df.volume)
        df["OSMA_20"] = ta.MA(df['OBV'], timeperiod=20)
        df['ST'] = pdta.supertrend(high=df.high, low=df.low, close=df.close, period=7, multiplier=2)['SUPERT_7_2.0']
        df['BUY'] = df['SELL'] = df['V_DOWN'] = df['V_UP'] = 0
        df = df.round(decimals=2)
        trade = {"symbol": None, "buy/sell": None, "entry": None, "entry date": None, "exit": None, "exit date": None, "target": None, 'sl': None}
        # print(df)
        position = None
        for i in df.index[20:]:
            if df['close'][i-1] < df['VWAP'][i-1] and df['close'][i] > df['VWAP'][i] and df['RSI'][i] > df["REMA_9"][i] and df['OBV'][i] > df["OSMA_20"][i] and df['close'][i] > df['ST'][i] and position != "buy":
                if trade["symbol"] is not None and (df['close'][i] > trade['target'] or df['close'][i] < trade['sl']):
                    if df['close'][i] > trade['target']:
                        trade["exit"] = trade['target']
                    if df['close'][i] < trade['sl']:
                        trade["exit"] = trade['target']
                    trade["exit date"] = df["timestamp"][i]
                    all_trades.append(copy.deepcopy(trade))
                if position is not None:
                    trade["symbol"] = symbol
                    trade["buy/sell"] = "buy"
                    trade['qty'] = fy_lib.N50_FUT_LOTSIZE[symbol]
                    trade["entry"] = df["close"][i]
                    trade['sl'] = (0.995 * trade['entry'])
                    trade['target'] = (1.005 * trade['entry'])
                    trade["entry date"] = df["timestamp"][i]
                position = "buy"
            if df['close'][i-1] > df['VWAP'][i-1] and df['close'][i] < df['VWAP'][i] and df['RSI'][i] < df["REMA_9"][i] and df['OBV'][i] < df["OSMA_20"][i] and df['close'][i] < df['ST'][i] and position != "Sell":
                if trade["symbol"] is not None and ( df['close'][i] < trade['target'] or df['close'][i] > trade['sl']):
                    if df['close'][i] > trade['target']:
                        trade["exit"] = trade['target']
                    if df['close'][i] < trade['sl']:
                        trade["exit"] = trade['target']
                    trade["exit date"] = df["timestamp"][i]
                    all_trades.append(copy.deepcopy(trade))
                if position is not None:
                    trade["symbol"] = symbol
                    trade["buy/sell"] = "sell"
                    trade['qty'] = fy_lib.N50_FUT_LOTSIZE[symbol]
                    trade["entry"] = df["close"][i]
                    trade['sl'] = (1.005 * trade['entry'])
                    trade['target'] = (0.995 * trade['entry'])
                    trade["entry date"] = df["timestamp"][i]
                position = "sell"
    return all_trades

symbol_list = [name[:-3]+ '21NOVFUT' for name in fy_lib.N50_LIST]

data = symbols_backtesting(symbol_list)
if data:
    risk_percent = 5/100
    df = pd.DataFrame(data)
    df["P/L"] = np.where(df["buy/sell"] == "buy", ((df["exit"] - df["entry"])*df["qty"]), ((df["entry"] - df["exit"])*df["qty"]))
    # df = df[df["buy/sell"] =="buy"].reset_index(drop=True)

    df["Probability"] = 100*(np.where(df["P/L"] > 0, 1, 0).cumsum())/(np.where(df["P/L"] != np.NaN, 1, 0).cumsum())
    df["Return"] = df["P/L"].cumsum()
    df["DrawDown"] = df["Return"] - (df["Return"].cummax().apply(lambda X: X if X > 0 else 0))

    print(df)
    df.to_csv("D:/bhave/Desktop/backtest.csv", mode='a', header=True, index=False)
else:
    print("No Trade")