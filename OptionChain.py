import fy_lib
import os
import pandas as pd
import sys
import warnings
import xlwings as xw
from datetime import time, datetime
from time import sleep

from fyers_apiv3 import fyersModel

pd.set_option('display.max_columns', None)
warnings.filterwarnings('ignore')

wb = xw.Book(r'D:\bhave\Desktop\PyProgram\Optionchain.xlsm')
sheet = wb.sheets['OC']  # change sheet name


def OptionChain():
    try:
        token = fy_lib.read_file()
    except FileNotFoundError:
        print('Getting the access token!')
        fy_lib.get_access_token()
        sys.exit()
    fyers = fyersModel.FyersModel(client_id=fy_lib.fyers_api_id_BBP, is_async=False, token=token, log_path=os.getcwd())
    response = fyers.get_profile()
    if 'error' in response['s'] or 'error' in response['message'] or 'expired' in response['message']:
        print('Getting a access token!')
        fy_lib.get_access_token()
    else:
        print('You already have a access token!')
        print(response)
    # fyers = login()
    while datetime.now().time() < time(23, 30):
        for symbol in fy_lib.oc_data:
            data = {
                "symbol": fy_lib.oc_data[symbol]["Symbol"], # "NSE:NIFTY50-INDEX" "NSE:NIFTYBANK-INDEX" "BSE:SENSEX-INDEX" "BSE:BANKEX-INDEX" "NSE:FINNIFTY-INDEX"
                "strikecount": 20,
                "timestamp": ""
            }
            optRes = fyers.optionchain(data=data)
            # print(optRes)

            vix = optRes['data']['indiavixData']['ltp']
            pcr = optRes['data']['putOi'] / optRes['data']['callOi']
            optdf = pd.DataFrame(optRes['data']['optionsChain'])
            exchange = optdf["exchange"]
            spotLtp = optdf[optdf.exchange == exchange]['ltp'].iloc[0]
            optdf = optdf[optdf.option_type.isin(['CE', 'PE'])]
            optdf = optdf.dropna(axis=1, how='all')
            optdf['Strike'] = optdf['strike_price']
            del optdf['strike_price'], optdf['fyToken']
            cedf = optdf[optdf.option_type == 'CE']
            pedf = optdf[optdf.option_type == 'PE']
            ocdf = pd.merge(cedf, pedf, on='Strike', suffixes=['_CE', '_PE'])
            ocdf = ocdf.sort_values(by='Strike')
            # # display in excel
            sheet = wb.sheets[symbol]
            # sheet.clear_contents()
            # print(ocdf.head(2))
            sheet['N1'].value = ['Spot', 'Vix', 'PCR']
            sheet['N2'].value = [spotLtp, vix, pcr]
            sheet['f4'].value = ocdf
        print(f"last update at {datetime.now()}")
        sleep(fy_lib.RefreshRate)


if __name__ == '__main__':
    # interval = trade_time-now
    # print(f"Code run after {interval.total_seconds()} sec")
    # sleep(interval.total_seconds()) if interval.total_seconds() > 0 else sleep(0)
    OptionChain()
