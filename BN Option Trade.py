import threading
from datetime import timedelta, datetime
import pandas as pd
import pandas_ta as pdta
import talib as ta
import telegram_send
from time import sleep, time

import fy_lib

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

TimeFrame = 300
now = datetime.now()
trade_time = now.replace(hour=9, minute=25, second=3, microsecond=0)


def BNifty_history(symbol, resolution=5):
    BNifty_df = fy_lib.historical_data(symbol, delta=1, resolution=resolution)
    BNifty_df.set_index(pd.DatetimeIndex(BNifty_df["timestamp"]), inplace=True)
    BNifty_df['symbol'] = symbol
    BNifty_df["BBU"], BNifty_df["BBM"], BNifty_df["BBL"] = ta.BBANDS(BNifty_df.close, timeperiod=20, nbdevup=1, nbdevdn=1)
    BNifty_df['N_DOWN'] = BNifty_df['N_UP'] = BNifty_df['NP_UP'] = BNifty_df['NP_DOWN'] = 0
    BNifty_df = BNifty_df.round(decimals=2)
    for i in BNifty_df.timestamp:
        if BNifty_df['close'][i] < BNifty_df["BBL"][i]:
            BNifty_df['N_DOWN'].at[i] = 1
        if BNifty_df['close'][i] > BNifty_df["BBL"][i]:
            BNifty_df['NP_UP'].at[i] = 1
        if BNifty_df['close'][i] > BNifty_df["BBU"][i]:
            BNifty_df['N_UP'].at[i] = 1
        if BNifty_df['close'][i] < BNifty_df["BBU"][i]:
            BNifty_df['NP_DOWN'].at[i] = 1
    # Nifty_df.to_csv("D:/bhave/Desktop/n.csv", mode='a', header=True, index=False)
    print(BNifty_df.tail(2))
    return BNifty_df


def option_history(symbol):
    OPTION_df = fy_lib.historical_data(symbol, delta=1, resolution=5)
    OPTION_df.set_index(pd.DatetimeIndex(OPTION_df["timestamp"]), inplace=True)
    OPTION_df['symbol'] = symbol
    OPTION_df['VWAP'] = pdta.vwap(OPTION_df.high, OPTION_df.low, OPTION_df.close, OPTION_df.volume)
    OPTION_df["BBU"], OPTION_df["BBM"], OPTION_df["BBL"] = ta.BBANDS(OPTION_df.close, timeperiod=20, nbdevup=1, nbdevdn=1)
    OPTION_df['O_DOWN'] = 0
    OPTION_df = OPTION_df.round(decimals=2)
    for i in OPTION_df.timestamp:
        if OPTION_df['close'][i] < OPTION_df['VWAP'][i] and OPTION_df['close'][i] < OPTION_df["BBL"][i]:
            OPTION_df['O_DOWN'].at[i] = 1
    print(OPTION_df.tail(2))
    return OPTION_df


def checkSignal():
    start = time()
    print(datetime.fromtimestamp(start).strftime('%Y-%m-%d %H:%M:%S'))
    step_list = [50, 100, 150, 200]
    Symbol = "NSE:NIFTY"
    Expiery = '21NOV'
    ltp = BNifty_history("NSE:NIFTY21NOVFUT")['close'].iloc[-1]
    step_value = 50
    List = []
    for step in step_list:
        atm_strike = round(ltp / step_value) * step_value+step
        ce_option_name = [Symbol+Expiery+str(atm_strike)+'CE']
        for i in ce_option_name:
            if i not in List:
                List.append(i)
    for step in step_list:
        atm_strike = round(ltp / step_value) * step_value-step
        pe_option_name = [Symbol+Expiery+str(atm_strike)+'PE']
        for i in pe_option_name:
            if i not in List:
                List.append(i)
    for symbol in List:
        print(symbol)
        lt = (pd.Timestamp.now(tz='Asia/Kolkata')-timedelta(minutes=5)).replace(second=0, microsecond=0)
        pt = (pd.Timestamp.now(tz='Asia/Kolkata')-timedelta(minutes=10)).replace(second=0, microsecond=0)
        O_df = option_history(symbol)
        N_df = BNifty_history("NSE:NIFTY21NOVFUT")
        if O_df is not None:
            O_candle = O_df.loc[lt]
            NL_candle = N_df.loc[lt]
            NP_candle = N_df.loc[pt]

            if NP_candle['NP_UP'] == 1 and O_candle['O_DOWN'] == 1 and NL_candle['N_DOWN'] == 1:
                trigerPrice = round(O_candle['close'], 1)
                orderPrice = round(trigerPrice-0.05, 2)
                stopTriger = orderPrice+20
                stopPrice = stopTriger+0.05



                telegram_send.send(messages=[f"SELL {symbol}\n{datetime.now()}"])
                print(f"SELL {symbol}\n{datetime.now()}")
            if NP_candle['NP_DOWN'] == 1 and O_candle['O_DOWN'] == 1 and NL_candle['N_UP'] == 1:
                trigerPrice = round(O_candle['close'], 1)
                orderPrice = round(trigerPrice-0.05, 2)
                stopTriger = orderPrice+20
                stopPrice = stopTriger+0.05

                telegram_send.send(messages=[f"SELL {symbol}\n{datetime.now()}"])
                print(f"SELL {symbol}\n{datetime.now()}")
    List.clear()
    Interval = TimeFrame-(time()-start)
    print(f"Next Scan {(pd.Timestamp.now(tz='Asia/Kolkata')+timedelta(minutes=5)).replace(second=0, microsecond=0)}")
    threading.Timer(Interval, checkSignal).start()


if __name__ == '__main__':
    interval = trade_time-now
    print(f"Code run after {interval.total_seconds()} sec")
    sleep(interval.total_seconds()) if interval.total_seconds() > 0 else sleep(0)
    checkSignal()
