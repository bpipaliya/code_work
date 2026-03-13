import pandas as pd
import requests
import json
import xlwings as xw
from time import sleep
from datetime import datetime, time, timedelta
import os
import numpy as np

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/92.0.4515.159 Safari/537.36', 'accept-language': 'en-IN,en;q=0.9,hi;q=0.8,gu;q=0.7',
           'accept-encoding': 'gzip, deflate, br'}
expiry = ""
excel_file = "OI.xlsx"
wb = xw.Book(excel_file)
sheet_oi_single = wb.sheets("OIData")
sht_live = wb.sheets("Data")
df_list = []
mp_list = []

oi_filename = os.path.join('Files', 'oi_data_records_{0}.json'.format(datetime.now().strftime("%d%m%y")))
mp_filename = os.path.join('Files', 'mp_data_records_{0}.json'.format(datetime.now().strftime("%d%m%y")))


def fetch_oi(df, mp_df):
    tries = 1
    max_retries = 1
    while tries <= max_retries:
        try:
            r = requests.get(url, headers=headers).json()
            # print(r)
            # with open("oidata.json", "w") as files:
            #     files.write(json.dumps(r, indent=4, sort_keys=True))

            if expiry:
                ce_values = [data['CE'] for data in r['records']['data'] if "CE" in data and str(data['expiryDate']).lower() == str(expiry).lower()]
                pe_values = [data['PE'] for data in r['records']['data'] if "PE" in data and str(data['expiryDate']).lower() == str(expiry).lower()]
            else:
                ce_values = [data['CE'] for data in r['filtered']['data'] if "CE" in data]
                pe_values = [data['PE'] for data in r['filtered']['data'] if "PE" in data]
            ce_data = pd.DataFrame(ce_values)
            pe_data = pd.DataFrame(pe_values)
            ce_data = ce_data.sort_values(['strikePrice'])
            pe_data = pe_data.sort_values(['strikePrice'])
            # print((ce_data))
            sheet_oi_single.range("A2").options(index=False, header=False).value = ce_data.drop(
                ['expiryDate', 'identifier', 'totalSellQuantity', 'totalBuyQuantity', 'bidQty', 'bidprice', 'askQty', 'askPrice',
                 'totalTradedVolume', 'underlyingValue', 'underlying'], axis=1)[['openInterest',
                                                                                'changeinOpenInterest','pchangeinOpenInterest',
                                                                                'impliedVolatility','lastPrice','change','pChange','strikePrice']]
            sheet_oi_single.range("I2").options(index=False, header=False).value = pe_data.drop(
                ['identifier', 'totalSellQuantity', 'totalBuyQuantity', 'bidQty', 'bidprice', 'askQty', 'askPrice',
                 'totalTradedVolume', 'underlyingValue', 'underlying', 'strikePrice', 'expiryDate'], axis=1)[['openInterest',
                                                                                'changeinOpenInterest','pchangeinOpenInterest',
                                                                                'impliedVolatility','lastPrice','change','pChange']]
            ce_data['type'] = 'CE'
            pe_data['type'] = 'PE'
            df1 = pd.concat([ce_data, pe_data])
            if len(df_list) > 0:
                df1['Time'] = df_list[-1][0]['Time']
            if len(df_list) > 0 and df1.to_dict('records') == df_list[-1]:
                print('Duplicate data, Not recording')
                sleep(10)
                tries += 1
                continue
            df1['Time'] = datetime.now().strftime('%H:%M')

            pcr = pe_data['totalTradedVolume'].sum()/ce_data['totalTradedVolume'].sum()
            mp_dict = {datetime.now().strftime('%H:%M'):{'underlying':df1['underlyingValue'].iloc[-1],
                                                         'MaxPain':wb.sheets('Dashboard').range('H8').value,
                                                         'pcr' : pcr,
                                                         'call_decay' : ce_data.nlargest(5, 'openInterest', keep='last')['change'].mean(),
                                                         'put_decay': pe_data.nlargest(5, 'openInterest', keep='last')['change'].mean()}}
            df3 = pd.DataFrame(mp_dict).transpose()
            mp_df = pd.concat([mp_df, df3])
            wb.sheets('MPData').range('A2').options(header=False).value = mp_df
            with open (mp_filename, "w") as files:
                files.write(json.dumps(mp_df.to_dict(), indent=4, sort_keys=True))
            if not df.empty:
                df = df[['strikePrice', 'expiryDate', 'underlying', 'identifier', 'openInterest', 'changeinOpenInterest',
                         'pchangeinOpenInterest', 'totalTradedVolume', 'impliedVolatility', 'lastPrice', 'change',
                         'pChange', 'totalBuyQuantity', 'totalSellQuantity', 'bidQty', 'bidprice', 'askQty', 'askPrice',
                         'underlyingValue', 'type', 'Time']]
            df1 = df1[['strikePrice', 'expiryDate', 'underlying', 'identifier', 'openInterest', 'changeinOpenInterest',
                     'pchangeinOpenInterest', 'totalTradedVolume', 'impliedVolatility', 'lastPrice', 'change', 'pChange',
                     'totalBuyQuantity', 'totalSellQuantity', 'bidQty', 'bidprice', 'askQty', 'askPrice',
                     'underlyingValue', 'type', 'Time']]
            df=pd.concat([df, df1])
            df_list.append(df1.to_dict('records'))
            with open (oi_filename, "w") as files:
                files.write(json.dumps(df_list, indent=4, sort_keys=True))
            return df, mp_df
        except Exception as error:
            print("error {0}".format(error))
            tries += 1
            sleep(10)
            continue

    if tries >= max_retries:
        print('Max_retries exceeded. No new data at time {0}'.format(datetime.now()))
        return df, mp_df


def main():
    global df_list
    try:
        df_list = json.loads(open(oi_filename).read())
    except Exception as error:
        print('Error reading data Error: {0}'.format(error))
        df_list = []
    if df_list:
        df = pd.DataFrame()
        for item in df_list:
            df = pd.concat([df, pd.DataFrame(item)])
    else:
        df = pd.DataFrame()
    try:
        mp_list = json.loads(open(mp_filename).read())
        mp_df = pd.DataFrame().from_dict(mp_list)
    except Exception as error:
        print('Error reading data Error: {0}'.format(error))
        mp_list = []
        mp_df = pd.DataFrame()

    timeframe = 5
    while time(9,15) <= datetime.now().time() <= time(15,30):
        timenow = datetime.now()
        check = True if int(datetime.strftime(timenow.min,'%M'))/timeframe in list(np.arange(0.0, 20.0)) else False
        if check:
            nextscan = timenow + timedelta(minutes = timeframe)
            df, mp_df = fetch_oi(df, mp_df)
            if not df.empty:
                df['impliedVolatility'] = df['impliedVolatility'].replace(to_replace=0, method='bfill').values
                df['identifier'] = df['strikePrice'].astype(str) + df['type']
                sht_live.range("A1").options(index=False).value = df
                wb.api.RefreshAll()
                waitsecs = int((nextscan - datetime.now()).seconds)
                print("wait for{0} seconds".format(waitsecs))
                sleep(waitsecs) if waitsecs > 0 else sleep(0)
            else:
                print("No data received")
                sleep(30)


if __name__ == '__main__':
    main()
