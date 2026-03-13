import credentials
from datetime import datetime, timedelta
import pandas as pd
import talib as ta
import fy_lib

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

SYMBOL_LIST = credentials.N50_LIST
SymbolAbove20 = []


def DailyData(symbol, resolution="D"):
    df = fy_lib.historical_data(symbol, delta=5, resolution=resolution)
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df = pd.DataFrame(df['candles'], columns=columns)
    df['timestamp'] = (pd.to_datetime(df[ 'timestamp' ], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    df['time'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M')
    df = df[['date', 'time', 'timestamp', 'open', 'high', 'low', 'close', 'volume']]
    df.drop('timestamp', axis=1, inplace=True)
    df['DSMA'] = ta.SMA(df['close'], timeperiod=20)
    df['Daily_UP'] = 0
    df = df.round(decimals=2)

    for i in range(2, len(df)):
        if df['close'][i] > df['DSMA'][i]:
            df['Daily_UP'].at[i] = 1

    # print(df.tail(1))
    return df
# #
def HrData(symbol, resolution=60):
    df = fy_lib.historical_data(symbol, delta=5, resolution=resolution)
    columns = [ 'timestamp', 'open', 'high', 'low', 'close', 'volume' ]
    Hr = pd.DataFrame(df [ 'candles' ], columns=columns)
    Hr [ 'timestamp' ] = (
        pd.to_datetime(Hr [ 'timestamp' ], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
    Hr [ 'date' ] = pd.to_datetime(Hr [ 'timestamp' ]).dt.date
    Hr [ 'time' ] = pd.to_datetime(Hr [ 'timestamp' ]).dt.strftime('%H:%M')
    Hr = Hr [ [ 'date', 'time', 'timestamp', 'open', 'high', 'low', 'close', 'volume' ] ]
    Hr.drop('timestamp', axis=1, inplace=True)
    Hr ['HSMA' ] = ta.SMA(Hr['close'], timeperiod=20)
    Hr [ 'Hr_UP' ] = 0
    Hr = Hr.round(decimals=2)

    for j in range(30, len(Hr)):
        if Hr['close'][j] > Hr['HSMA'][j]:
            Hr['Hr_UP'].at[j] = 1

    # print(Hr.tail(1))
    return Hr

def checkSignal():
    # start = time()
    global SymbolAbove20

    for symbol in SYMBOL_LIST:
        if symbol not in SymbolAbove20:
            # print(symbol)
            Daily_df = DailyData(symbol)
            Hr_df = HrData(symbol)

            if Daily_df is not None and Hr_df is not None:
                DailyCandle = Daily_df.iloc[-1]
                HrCandle = Hr_df.iloc [ -1 ]
                if DailyCandle['Daily_UP'] == 1 and HrCandle['Hr_UP'] == 1:
                    print(f'{symbol} is above DSMA AND HSMA')


if __name__ == '__main__':
    # interval = StartTime - datetime.now()
    # print(f"Code run after {interval.total_seconds() if interval.total_seconds() > 0 else sleep(0)} sec")
    # sleep(interval.total_seconds()) if interval.total_seconds() > 0 else sleep(0)
    checkSignal()