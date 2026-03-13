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
        df = fy_lib.historical_data(symbol, delta=5, resolution=15)
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
        trade = {"buy_symbol": None, 'buy_qty': None, "buy": None, "buy_entry": None, "buy_entry date": None, "buy_exit": None, "buy_exit date": None, "buy_target": None, 'buy_sl': None} # , "sell_symbol": None, 'sell_qty': None, "sell": None,"sell_entry": None, "sell_entry date": None, "sell_exit": None, "sell_exit date": None, "sell_target": None, 'sell_sl': None}
        # print(df)
        Buy_position = None
        Sell_position = None
        for i in df.index[20:]:
            if trade["buy_symbol"] is not None and (df['close'][i] > trade['buy_target'] or df['close'][i] < trade['buy_sl']):
                if df['close'][i] > trade['buy_target']:
                    trade["buy_exit"] = trade['buy_target']
                if df['close'][i] < trade['buy_sl']:
                    trade["exit"] = trade['buy_target']
                trade["buy_exit date"] = df["timestamp"][i]
                all_trades.append(copy.deepcopy(trade))
                Buy_position = None
            if Buy_position is None and df['close'][i-1] < df['VWAP'][i-1] and df['close'][i] > df['VWAP'][i] and df['RSI'][i] > df["REMA_9"][i] and df['OBV'][i] > df["OSMA_20"][i] and df['close'][i] > df['ST'][i]:
                trade["buy_symbol"] = symbol
                trade["buy"] = "buy"
                trade['buy_qty'] = fy_lib.N50_FUT_LOTSIZE[symbol]
                trade["buy_entry"] = df["close"][i]
                trade['buy_sl'] = (0.995 * trade['buy_entry'])
                trade['buy_target'] = (1.005 * trade['buy_entry'])
                trade["buy_entry date"] = df["timestamp"][i]
                Buy_position = "buy"

            # if trade["sell_symbol"] is not None and (df['close'][i] < trade['sell_target'] or df['close'][i] > trade['sell_sl']):
            #     if df['close'][i] > trade['sell_target']:
            #         trade["sell_exit"] = trade['sell_target']
            #     if df['close'][i] < trade['sell_sl']:
            #         trade["sell_exit"] = trade['sell_target']
            #     trade["sell_exit date"] = df["timestamp"][i]
            #     all_trades.append(copy.deepcopy(trade))
            #     Sell_position = None
            # if df['close'][i-1] > df['VWAP'][i-1] and df['close'][i] < df['VWAP'][i] and df['RSI'][i] < df["REMA_9"][i] and df['OBV'][i] < df["OSMA_20"][i] and df['close'][i] < df['ST'][i]:
            #     if Sell_position is None:
            #         trade["sell_symbol"] = symbol
            #         trade["sell"] = "sell"
            #         trade['sell_qty'] = fy_lib.N50_FUT_LOTSIZE[symbol]
            #         trade["sell_entry"] = df["close"][i]
            #         trade['sell_sl'] = (1.005 * trade['sell_entry'])
            #         trade['sell_target'] = (0.995 * trade['sell_entry'])
            #         trade["sell_entry date"] = df["timestamp"][i]
            #         Sell_position = "sell"


    return all_trades

symbol_list = [name[:-3]+ '21NOVFUT' for name in fy_lib.N50_LIST]

data = symbols_backtesting(symbol_list)

df = pd.DataFrame(data)
df.to_csv("D:/bhave/Desktop/b.csv", mode='a', header=True, index=False)
print(df)
# if data:
#     risk_percent = 5/100
#     df = pd.DataFrame(data)
#     df["P/L"] = np.where(df["buy"] == "buy", ((df["exit"] - df["entry"])*df["qty"]), ((df["entry"] - df["exit"])*df["qty"]))
#     # df = df[df["buy/sell"] =="buy"].reset_index(drop=True)
#
#     df["Probability"] = 100*(np.where(df["P/L"] > 0, 1, 0).cumsum())/(np.where(df["P/L"] != np.NaN, 1, 0).cumsum())
#     df["Return"] = df["P/L"].cumsum()
#     df["DrawDown"] = df["Return"] - (df["Return"].cummax().apply(lambda X: X if X > 0 else 0))
#
#     print(df)
#     df.to_csv("D:/bhave/Desktop/backtest.csv", mode='a', header=True, index=False)
# else:
#     print("No Trade")