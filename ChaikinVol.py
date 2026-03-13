import numpy as np
import pandas as pd
import time
from _datetime import datetime, timedelta
from fyers_api import fyersModel
import fy_lib

app_id = fyers_lib.fyers_api2_id_BBP
app_secret = fyers_lib.fyers_api2_secret_BBP
redirect_url = fyers_lib.fyers_redirect_url
password = fyers_lib.fyers_pwd_BBP
two_fa = fyers_lib.fyers_two_fa_BBP
user_id = fyers_lib.fyers_user_id_BBP
access_token = open("access_token2_BBP.txt", "r").read()
SYMBOL_LIST = []
TimeFrame = 300

fyers = fyersModel.FyersModel(client_id=app_id, token=access_token, log_path="E:\\bhave\\Desktop")

def getHistoricalData(symbol, resolution=TimeFrame):
    from_date = datetime.now() - timedelta(days=3)
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
    df = df [ [ 'timestamp', 'open', 'high', 'low', 'close', 'volume' ] ]
    return df


def ExpMovingAverage(values, window):
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    a =  np.convolve(values, weights, mode='full')[:len(values)]
    a[:window] = a[window]
    return a
def percentChange(startPoint, currentPoint):
    return ((float(currentPoint)-startPoint)/abs(startPoint))*100.00

def chaikinVolCalc(emaUsed, periodAgo):
    chaikin_volatility = []
    highMlow = []
    x = 0

    while x < len(date):
        hml = high[x] - low[x]
        highMlow.append(hml)
        x +=1

    highMlowEMA = ExpMovingAverage(highMlow, emaUsed)
    y = emaUsed + periodAgo
    while y < len(date):
        cvc = percentChange(highMlowEMA[y-periodAgo], highMlowEMA[y])

        chaikin_volatility.append(cvc)
        y+=1

    return date[emaUsed+periodAgo:], chaikin_volatility
chaikinVolCalc((10,10))