import time
import fy_lib
from datetime import timedelta, date
import pandas as pd
from fyers_api import fyersModel

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

app_id = fy_lib.fyers_api2_id_BBP
app_secret = fy_lib.fyers_api2_secret_BBP
redirect_url = fy_lib.fyers_redirect_url
password = fy_lib.fyers_pwd_BBP
two_fa = fy_lib.fyers_two_fa_BBP
user_id = fy_lib.fyers_user_id_BBP
access_token = fy_lib.access_token_BBP

start_date = date(2021, 8, 25)   # yyyy-mm-dd format
end_date = date(2021, 8, 26)     # yyyy-mm-dd format

fyers = fyersModel.FyersModel(client_id=app_id, token=access_token, log_path="D:\\Coding\\Fyers")

start = time.time()
symbol_df = fy_lib.N50_LIST
for i in range(0, len(symbol_df)):
    start1 = time.time()
    symbol = symbol_df.loc[i]['symbol']
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    final_df = pd.DataFrame(columns=columns)
    from_date = start_date

    while from_date < end_date:
        to_date = from_date + timedelta(days=100)
        from_date_format = from_date.strftime("%Y-%m-%d")
        to_date_format = to_date.strftime("%Y-%m-%d")
        data = {
            "symbol": symbol,
            "resolution": 5,
            "date_format": 1,
            "range_from": from_date_format,
            "range_to": to_date_format,
            "cont_flag": 1
        }
        candle_json = fyers.history(data)
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        df = pd.DataFrame(candle_json['candles'], columns=columns)

        final_df = final_df.append(df, ignore_index=True)
        from_date = from_date + timedelta(days=101)

    final_df['timestamp'] = pd.to_datetime(final_df['timestamp'], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata')
    final_df['date'] = pd.to_datetime(final_df['timestamp']).dt.date
    final_df['time'] = pd.to_datetime(final_df['timestamp']).dt.strftime('%H:%M')
    final_df['symbol'] = symbol_df.loc[i]['symbol']
    final_df.drop('timestamp', axis=1, inplace=True)
    final_df = final_df[['symbol', 'date', 'time', 'open', 'high', 'low', 'close', 'volume']]

    filename = str(symbol_df.loc[i]['token']) + '.txt'
    # final_df.to_csv(f'D:\\Coding\\Fyers\\Data\\Data.csv', mode='a', header=False)
    print(time.time() - start1)
    print(final_df)
print(time.time() - start)
