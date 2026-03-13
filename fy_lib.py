import base64
import os
import sys

import pandas as pd
import pyotp
import requests
from datetime import datetime, timedelta
from time import sleep
from urllib.parse import parse_qs, urlparse

from fyers_apiv3 import fyersModel

fyers_user_id_BBP = 'XB01059'
fyers_totp_key_BBP = "4JAOSAZMBDYVS3IGONCPN7XKSHKIMJXK"
fyers_api_id_BBP = 'E8KC42WAM1-100'
fyers_api_secret_BBP = 'MSRD7PRWLE'
fyers_pin_BBP = "8931"
fyers_redirect_uri_BBP = "https://trade.fyers.in/api-login/redirect-uri/index.html"


def read_file():
    with open("access_token_BBP.txt", "r") as f:
        token = f.read()
    return token


def write_file(token):
    with open('access_token_BBP.txt', 'w') as f:
        f.write(token)


def getEncodedString(string):
    string = str(string)
    base64_bytes = base64.b64encode(string.encode("ascii"))
    return base64_bytes.decode("ascii")


def get_access_token():
    URL_SEND_LOGIN_OTP = "https://api-t2.fyers.in/vagator/v2/send_login_otp_v2"
    res = requests.post(url=URL_SEND_LOGIN_OTP,
                        json={"fy_id": getEncodedString(fyers_user_id_BBP), "app_id": "2"}).json()

    if datetime.now().second % 30 > 27: sleep(5)
    URL_VERIFY_OTP = "https://api-t2.fyers.in/vagator/v2/verify_otp"
    res2 = requests.post(url=URL_VERIFY_OTP,
                         json={"request_key": res["request_key"], "otp": pyotp.TOTP(
                             fyers_totp_key_BBP).now()}).json()
    ses = requests.Session()
    URL_VERIFY_OTP2 = "https://api-t2.fyers.in/vagator/v2/verify_pin_v2"
    payload2 = {"request_key": res2["request_key"], "identity_type": "pin", "identifier": getEncodedString(
        fyers_pin_BBP)}
    res3 = ses.post(url=URL_VERIFY_OTP2, json=payload2).json()

    ses.headers.update({
        'authorization': f"Bearer {res3['data']['access_token']}"
    })
    TOKENURL = "https://api-t1.fyers.in/api/v3/token"
    payload3 = {"fyers_id": fyers_user_id_BBP,
                "app_id": fyers_api_id_BBP[:-4],
                "redirect_uri": fyers_redirect_uri_BBP,
                "appType": "100", "code_challenge": "",
                "state": "None", "scope": "", "nonce": "", "response_type": "code", "create_cookie": True}

    res3 = ses.post(url=TOKENURL, json=payload3).json()
    url = res3['Url']
    parsed = urlparse(url)
    auth_code = parse_qs(parsed.query)['auth_code'][0]

    grant_type = "authorization_code"
    response_type = "code"
    session = fyersModel.SessionModel(
        client_id=fyers_api_id_BBP,
        secret_key=fyers_api_secret_BBP,
        redirect_uri=fyers_redirect_uri_BBP,
        response_type=response_type,
        grant_type=grant_type
    )
    session.set_token(auth_code)
    response = session.generate_token()
    token = response['access_token']
    write_file(token)
    # fyers = fyersModel.FyersModel(client_id=fyers_api_id_BBP, is_async=False, token=read_file(), log_path=os.getcwd())
    # return fyers

RefreshRate = 180
oc_data ={
        "NIFTY": {"SheetName": "NIFTY", "Symbol": "NSE:NIFTY50-INDEX", "Expiry": "2024-05-16", "NoOfStrike": "10"},
        "N_BANK": {"SheetName": "N_BANK", "Symbol": "NSE:NIFTYBANK-INDEX", "Expiry": "2024-05-15", "NoOfStrike": "10"},
        "BANKEX": {"SheetName": "BANKEX", "Symbol": "BSE:BANKEX-INDEX", "Expiry": "2024-05-13", "NoOfStrike": "10"},
        "SENSEX": {"SheetName": "SENSEX", "Symbol": "BSE:SENSEX-INDEX", "Expiry": "2024-05-17", "NoOfStrike": "10"},
        "FINNIFTY": {"SheetName": "FINNIFTY", "Symbol": "NSE:FINNIFTY-INDEX", "Expiry": "2024-05-14", "NoOfStrike": "10"}
    }

# def place_BO_order(symbol, qty, side, limitPrice, stopPrice, stopLoss, takeProfit):
#     data = {
#         "symbol": symbol,
#         "qty": qty,
#         "type": 4,  # 1 = Limit Order, 2 = Market Order, 3 = Stop Order (SL-M), 4 = Stoplimit Order (SL-L)
#         "side": side,  # 1 = buy, -1 = sell
#         "productType": "BO",  # CNC=equity only, INTRADAY=all segments, MARGIN=derivatives, CO=Cover O, BO=Bracket O
#         "limitPrice": limitPrice,
#         "stopPrice": stopPrice,  # Provide valid price for CO and BO orders
#         "validity": "DAY",
#         "disclosedQty": 0,
#         "offlineOrder": "False",
#         "stopLoss": stopLoss,
#         "takeProfit": takeProfit  # Provide valid price for CO and BO orders
#     }
#     fyers.place_order(data)
# 
# 
# def place_CO_order(symbol, qty: int, side: int, limitPrice: float, stopLoss: float):
#     data = {
#         "symbol": symbol,
#         "qty": qty,
#         "type": 1,  # 1 = Limit Order, 2 = Market Order, 3 = Stop Order (SL-M), 4 = Stoplimit Order (SL-L)
#         "side": side,  # 1 = buy, -1 = sell
#         "productType": "CO",   # CNC=equity only, INTRADAY=all segments, MARGIN=derivatives, CO=Cover O, BO=Bracket O
#         "limitPrice": limitPrice,
#         "stopPrice": 0,  # Provide valid price for CO and BO orders
#         "validity": "DAY",
#         "disclosedQty": 0,
#         "offlineOrder": "False",
#         "stopLoss": stopLoss,
#         "takeProfit": 0  # Provide valid price for CO and BO orders
#     }
#     fyers.place_order(data)
# 
# 
# def place_SL_order(symbol, qty: int, side: int, stopPrice: float, limitPrice: float):
#     data = {
#         "symbol": symbol,
#         "qty": qty,
#         "type": 4,  # 1 = Limit Order, 2 = Market Order, 3 = Stop Order (SL-M), 4 = Stoplimit Order (SL-L)
#         "side": side,  # 1 = buy, -1 = sell
#         "productType": "MARGIN",  # CNC=equity only, INTRADAY=all segments, MARGIN=derivatives, CO=Cover O, BO=Bracket O
#         "limitPrice": limitPrice,
#         "stopPrice": stopPrice,  # Provide valid price for CO and BO orders
#         "validity": "DAY",
#         "disclosedQty": 0,
#         "offlineOrder": "False",
#         "stopLoss": 0,
#         "takeProfit": 0  # Provide valid price for CO and BO orders
#     }
#     fyers.place_order(data)
# 
# 
# def place_BP_order(symbol, qty: int, side: int, limitPrice: float):
#     data = {
#         "symbol": symbol,
#         "qty": qty,
#         "type": 3,  # 1 = Limit Order, 2 = Market Order, 3 = Stop Order (SL-M), 4 = Stoplimit Order (SL-L)
#         "side": side,  # 1 = buy, -1 = sell
#         "productType": "MARGIN",  # CNC=equity only, INTRADAY=all segments, MARGIN=derivatives, CO=Cover O, BO=Bracket O
#         "limitPrice": limitPrice,
#         "stopPrice": 0,  # Provide valid price for CO and BO orders
#         "validity": "DAY",
#         "disclosedQty": 0,
#         "offlineOrder": "False",
#         "stopLoss": 0,
#         "takeProfit": 0  # Provide valid price for CO and BO orders
#     }
#     fyers.place_order(data)
# 
# 
# def place_L_order(symbol, qty: int, side: int, limitPrice: float):
#     data = {
#         "symbol": symbol,
#         "qty": qty,
#         "type": 1,  # 1 = Limit Order, 2 = Market Order, 3 = Stop Order (SL-M), 4 = Stoplimit Order (SL-L)
#         "side": side,  # 1 = buy, -1 = sell
#         "productType": "MARGIN",  # CNC=equity only, INTRADAY=all segments, MARGIN=derivatives, CO=Cover O, BO=Bracket O
#         "limitPrice": limitPrice,
#         "stopPrice": 0,  # Provide valid price for CO and BO orders
#         "validity": "DAY",
#         "disclosedQty": 0,
#         "offlineOrder": "False",
#         "stopLoss": 0,
#         "takeProfit": 0  # Provide valid price for CO and BO orders
#     }
#     fyers.place_order(data)
# 
# 
def historical_data(symbol, delta, resolution):
    # try:
    #     token = read_file()
    # except FileNotFoundError:
    #     print('Getting the access token!')
    #     get_access_token()
    #     sys.exit()
    # fyers = fyersModel.FyersModel(client_id=fyers_api_id_BBP, is_async=False, token=token, log_path=os.getcwd())
    # response = fyers.get_profile()
    # if 'error' in response['s'] or 'error' in response['message'] or 'expired' in response['message']:
    #     print('Getting a access token!')
    #     get_access_token()
    # else:
    #     print('You already have a access token!')
    #     # print(response)
    fyers = fyersModel.FyersModel(client_id=fyers_api_id_BBP, is_async=False, token=read_file, log_path=os.getcwd())
    from_date = (datetime.now()-timedelta(days=delta)).strftime("%Y-%m-%d")
    to_date = (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d")
    data = {
        "symbol": symbol,
        "resolution": resolution,
        "date_format": 1,
        "range_from": from_date,
        "range_to": to_date,
        "cont_flag": 0
    }
    df = fyers.history(data)
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df = pd.DataFrame(df['candles'], columns=columns)
    df['timestamp'] = (pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
    return df
    # try:
    #     fyers = fyersModel.FyersModel(client_id=fyers_api_id_BBP, is_async=False, token=read_file, log_path=os.getcwd())
    #     from_date = (datetime.now()-timedelta(days=delta)).strftime("%Y-%m-%d")
    #     to_date = (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d")
    #     data = {
    #         "symbol": symbol,
    #         "resolution": resolution,
    #         "date_format": 1,
    #         "range_from": from_date,
    #         "range_to": to_date,
    #         "cont_flag": 0
    #     }
    #     df = fyers.history(data)
    #     print(df)
    # except'error' in df['s'] or 'error' in df['message'] or 'expired' in df['message']:
    #     print('Getting a access token!')
    #     get_access_token()
    #     fyers = fyersModel.FyersModel(client_id=fyers_api_id_BBP, is_async=False, token=read_file, log_path=os.getcwd())
    #     from_date = (datetime.now()-timedelta(days=delta)).strftime("%Y-%m-%d")
    #     to_date = (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d")
    #     data = {
    #         "symbol": symbol,
    #         "resolution": resolution,
    #         "date_format": 1,
    #         "range_from": from_date,
    #         "range_to": to_date,
    #         "cont_flag": 0
    #     }
    #     df = fyers.history(data)
    # finally:
    #     columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    #     df = pd.DataFrame(df['candles'], columns=columns)
    #     df['timestamp'] = (pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
    #     return df
        
    #     token = read_file()
    # except FileNotFoundError:
    #     print('Getting the access token!')
    #     get_access_token()
    #     sys.exit()
    # fyers = fyersModel.FyersModel(client_id=fyers_api_id_BBP, is_async=False, token=token, log_path=os.getcwd())
    # response = fyers.get_profile()
    # # if 'error' in response['s'] or 'error' in response['message'] or 'expired' in response['message']:
    #     print('Getting a access token!')
    #     get_access_token()
    # else:
        
    #     print('You already have a access token!')
        # print(response)
    # fyers = fyersModel.FyersModel(client_id=fyers_api_id_BBP, is_async=False, token=token, log_path=os.getcwd())
    # from_date = (datetime.now()-timedelta(days=delta)).strftime("%Y-%m-%d")
    # to_date = (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d")
    # data = {
    #     "symbol": symbol,
    #     "resolution": resolution,
    #     "date_format": 1,
    #     "range_from": from_date,
    #     "range_to": to_date,
    #     "cont_flag": 0
    # }
    # df = fyers.history(data)
    # columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    # df = pd.DataFrame(df['candles'], columns=columns)
    # df['timestamp'] = (pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
    # return df



INDEX = ['NSE:NIFTY', 'NSE:BANKNIFTY']
N50_LIST = ["NSE:ADANIPORTS-EQ", 'NSE:AXISBANK-EQ', 'NSE:BAJAJ-AUTO-EQ', 'NSE:BAJAJFINSV-EQ',
            'NSE:BAJFINANCE-EQ', 'NSE:BHARTIARTL-EQ', 'NSE:BPCL-EQ', 'NSE:CIPLA-EQ', 'NSE:COALINDIA-EQ',
            'NSE:DIVISLAB-EQ', 'NSE:DRREDDY-EQ', 'NSE:EICHERMOT-EQ', 'NSE:GRASIM-EQ', 'NSE:HCLTECH-EQ',
            'NSE:HDFCBANK-EQ', 'NSE:HDFCLIFE-EQ', 'NSE:HEROMOTOCO-EQ', 'NSE:HINDALCO-EQ',
            'NSE:HINDUNILVR-EQ', 'NSE:ICICIBANK-EQ', 'NSE:INDUSINDBK-EQ', 'NSE:INFY-EQ', 'NSE:IOC-EQ', 'NSE:ITC-EQ',
            'NSE:JSWSTEEL-EQ', 'NSE:KOTAKBANK-EQ', 'NSE:LT-EQ', 'NSE:M&M-EQ', 'NSE:MARUTI-EQ', 'NSE:NESTLEIND-EQ',
            'NSE:NTPC-EQ', 'NSE:ONGC-EQ', 'NSE:POWERGRID-EQ', 'NSE:RELIANCE-EQ', 'NSE:SBILIFE-EQ', 'NSE:SBIN-EQ',
            'NSE:SHREECEM-EQ', 'NSE:SUNPHARMA-EQ', 'NSE:TATACONSUM-EQ', 'NSE:TATAMOTORS-EQ', 'NSE:TATASTEEL-EQ',
            "NSE:TCS-EQ",'NSE:TITAN-EQ', 'NSE:ULTRACEMCO-EQ', 'NSE:UPL-EQ', 'NSE:WIPRO-EQ']
N50_FUT_LOTSIZE = {'NSE:AARTIIND21DECFUT': 850, 'NSE:ABFRL21DECFUT': 2600, 'NSE:ACC21DECFUT': 500,
                   'NSE:ADANIENT21DECFUT': 1000, 'NSE:ADANIPORTS21DECFUT': 1250, 'NSE:ALKEM21DECFUT': 200,
                   'NSE:AMARAJABAT21DECFUT': 1000, 'NSE:AMBUJACEM21DECFUT': 3000, 'NSE:APLLTD21DECFUT': 550,
                   'NSE:APOLLOHOSP21DECFUT': 250, 'NSE:APOLLOTYRE21DECFUT': 2500, 'NSE:ASHOKLEY21DECFUT': 4500,
                   'NSE:ASTRAL21DECFUT': 275, 'NSE:AUBANK21DECFUT': 500,
                   'NSE:AUROPHARMA21DECFUT': 650, 'NSE:AXISBANK21DECFUT': 1200, 'NSE:BAJAJ-AUTO21DECFUT': 250,
                   'NSE:BAJAJFINSV21DECFUT': 75, 'NSE:BAJFINANCE21DECFUT': 125, 'NSE:BALKRISIND21DECFUT': 400,
                   'NSE:BANDHANBNK21DECFUT': 1800, 'NSE:BANKBARODA21DECFUT': 11700, 'NSE:BATAINDIA21DECFUT': 550,
                   'NSE:BEL21DECFUT': 3800, 'NSE:BERGEPAINT21DECFUT': 1100, 'NSE:BHARATFORG21DECFUT': 1500,
                   'NSE:BHARTIARTL21DECFUT': 1886, 'NSE:BHEL21DECFUT': 10500, 'NSE:BIOCON21DECFUT': 2300,
                   'NSE:BOSCHLTD21DECFUT': 50, 'NSE:BPCL21DECFUT': 1800, 'NSE:BRITANNIA21DECFUT': 200,
                   'NSE:CADILAHC21DECFUT': 2200, 'NSE:CANBK21DECFUT': 5400, 'NSE:CHOLAFIN21DECFUT': 1250,
                   'NSE:CIPLA21DECFUT': 650, 'NSE:COALINDIA21DECFUT': 4200, 'NSE:COFORGE21DECFUT': 200,
                   'NSE:COLPAL21DECFUT': 350, 'NSE:CONCOR21DECFUT': 1563, 'NSE:COROMANDEL21DECFUT': 625,
                   'NSE:CUB21DECFUT': 3100, 'NSE:CUMMINSIND21DECFUT': 600, 'NSE:DABUR21DECFUT': 1250,
                   'NSE:DEEPAKNTR21DECFUT': 500, 'NSE:DIVISLAB21DECFUT': 200, 'NSE:DLF21DECFUT': 3300,
                   'NSE:DRREDDY21DECFUT': 125, 'NSE:EICHERMOT21DECFUT': 350, 'NSE:ESCORTS21DECFUT': 550,
                   'NSE:EXIDEIND21DECFUT': 3600, 'NSE:FEDERALBNK21DECFUT': 10000, 'NSE:GAIL21DECFUT': 6100,
                   'NSE:GLENMARK21DECFUT': 1150, 'NSE:GMRINFRA21DECFUT': 22500, 'NSE:GODREJCP21DECFUT': 1000,
                   'NSE:GODREJPROP21DECFUT': 650, 'NSE:GRANULES21DECFUT': 1550, 'NSE:GRASIM21DECFUT': 475,
                   'NSE:GUJGASLTD21DECFUT': 1250, 'NSE:HAVELLS21DECFUT': 500, 'NSE:HCLTECH21DECFUT': 700,
                   'NSE:HDFC21DECFUT': 300, 'NSE:HDFCAMC21DECFUT': 200, 'NSE:HDFCBANK21DECFUT': 550,
                   'NSE:HDFCLIFE21DECFUT': 1100, 'NSE:HEROMOTOCO21DECFUT': 300, 'NSE:HINDALCO21DECFUT': 2150,
                   'NSE:HINDPETRO21DECFUT': 2700, 'NSE:HINDUNILVR21DECFUT': 300, 'NSE:IBULHSGFIN21DECFUT': 3100,
                   'NSE:ICICIBANK21DECFUT': 1375, 'NSE:ICICIGI21DECFUT': 425, 'NSE:ICICIPRULI21DECFUT': 1500,
                   'NSE:IDEA21DECFUT': 70000, 'NSE:IDFCFIRSTB21DECFUT': 9500, 'NSE:IGL21DECFUT': 1375,
                   'NSE:INDHOTEL21DECFUT': 3900, 'NSE:INDIGO21DECFUT': 500, 'NSE:INDUSINDBK21DECFUT': 900,
                   'NSE:INDUSTOWER21DECFUT': 2800, 'NSE:INFY21DECFUT': 600, 'NSE:IOC21DECFUT': 6500,
                   'NSE:IRCTC21DECFUT': 325, 'NSE:ITC21DECFUT': 3200, 'NSE:JINDALSTEL21DECFUT': 2500,
                   'NSE:JSWSTEEL21DECFUT': 1350, 'NSE:JUBLFOOD21DECFUT': 250, 'NSE:KOTAKBANK21DECFUT': 400,
                   'NSE:L&TFH21DECFUT': 8924, 'NSE:LALPATHLAB21DECFUT': 250, 'NSE:LICHSGFIN21DECFUT': 2000,
                   'NSE:LT21DECFUT': 575, 'NSE:LTI21DECFUT': 150, 'NSE:LTTS21DECFUT': 200, 'NSE:LUPIN21DECFUT': 850,
                   'NSE:M&M21DECFUT': 700, 'NSE:M&MFIN21DECFUT': 4000, 'NSE:MANAPPURAM21DECFUT': 6000,
                   'NSE:MARICO21DECFUT': 2000, 'NSE:MARUTI21DECFUT': 100, 'NSE:MCDOWELL-N21DECFUT': 1250,
                   'NSE:METROPOLIS21DECFUT': 200, 'NSE:MFSL21DECFUT': 650, 'NSE:MGL21DECFUT': 600,
                   'NSE:MINDTREE21DECFUT': 400, 'NSE:MOTHERSUMI21DECFUT': 3500, 'NSE:MPHASIS21DECFUT': 325,
                   'NSE:MRF21DECFUT': 10, 'NSE:MUTHOOTFIN21DECFUT': 750, 'NSE:NAM-INDIA21DECFUT': 1600,
                   'NSE:NATIONALUM21DECFUT': 17000, 'NSE:NAUKRI21DECFUT': 125, 'NSE:NAVINFLUOR21DECFUT': 225,
                   'NSE:NESTLEIND21DECFUT': 50, 'NSE:NMDC21DECFUT': 6700, 'NSE:NTPC21DECFUT': 5700,
                   'NSE:ONGC21DECFUT': 7700, 'NSE:PAGEIND21DECFUT': 30, 'NSE:PEL21DECFUT': 275,
                   'NSE:PETRONET21DECFUT': 3000, 'NSE:PFC21DECFUT': 6200, 'NSE:PFIZER21DECFUT': 125,
                   'NSE:PIDILITIND21DECFUT': 500, 'NSE:PIIND21DECFUT': 250, 'NSE:PNB21DECFUT': 16000,
                   'NSE:POWERGRID21DECFUT': 5333, 'NSE:PVR21DECFUT': 407, 'NSE:RAMCOCEM21DECFUT': 850,
                   'NSE:RBLBANK21DECFUT': 2900, 'NSE:RECLTD21DECFUT': 6000, 'NSE:RELIANCE21DECFUT': 250,
                   'NSE:SAIL21DECFUT': 9500, 'NSE:SBILIFE21DECFUT': 750, 'NSE:SBIN21DECFUT': 1500,
                   'NSE:SHREECEM21DECFUT': 25, 'NSE:SIEMENS21DECFUT': 275, 'NSE:SRF21DECFUT': 125,
                   'NSE:SRTRANSFIN21DECFUT': 400, 'NSE:STAR21DECFUT': 675, 'NSE:SUNPHARMA21DECFUT': 1400,
                   'NSE:SUNTV21DECFUT': 1500, 'NSE:TATACHEM21DECFUT': 1000, 'NSE:TATACONSUM21DECFUT': 1350,
                   'NSE:TATAMOTORS21DECFUT': 2850, 'NSE:TATAPOWER21DECFUT': 6750, 'NSE:TATASTEEL21DECFUT': 850,
                   'NSE:TCS21DECFUT': 300, 'NSE:TECHM21DECFUT': 600, 'NSE:TITAN21DECFUT': 375,
                   'NSE:TORNTPHARM21DECFUT': 250, 'NSE:TORNTPOWER21DECFUT': 1500, 'NSE:TRENT21DECFUT': 725,
                   'NSE:TVSMOTOR21DECFUT': 1400, 'NSE:UBL21DECFUT': 700, 'NSE:ULTRACEMCO21DECFUT': 100,
                   'NSE:UPL21DECFUT': 1300, 'NSE:VEDL21DECFUT': 3100, 'NSE:VOLTAS21DECFUT': 500,
                   'NSE:WIPRO21DECFUT': 1600, 'NSE:ZEEL21DECFUT': 3000, 'NSE:CANFINHOME21DECFUT': 975,
                   'NSE:DIXON21DECFUT': 125, 'NSE:HAL21DECFUT': 475, 'NSE:IEX21DECFUT': 1250,
                   'NSE:INDIAMART21DECFUT': 75, 'NSE:IPCALAB21DECFUT': 225, 'NSE:MCX21DECFUT': 350,
                   'NSE:OFSS21DECFUT': 125, 'NSE:POLYCAB21DECFUT': 300, 'NSE:SYNGENE21DECFUT': 850,
                   'NSE:ABBOTINDIA21DECFUT': 25, 'NSE:CROMPTON21DECFUT': 1100, 'NSE:DALBHARAT21DECFUT': 250,
                   'NSE:DELTACORP21DECFUT': 2300, 'NSE:INDIACEM21DECFUT': 2900, 'NSE:JKCEMENT21DECFUT': 175,
                   'NSE:OBEROIRLTY21DECFUT': 700, 'NSE:PERSISTENT21DECFUT': 150}
N50 = ['NIFTY', 'BANKNIFTY', 'ADANIPORTS', 'AXISBANK', 'BAJAJ-AUTO', 'BAJAJFINSV', 'BAJFINANCE', 'BHARTIARTL', 'BPCL',
       'CIPLA', 'COALINDIA', 'DIVISLAB', 'DRREDDY', 'EICHERMOT', 'GRASIM', 'HCLTECH', 'HDFCBANK', 'HDFC',
       'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDUNILVR', 'ICICIBANK', 'INDUSINDBK', 'INFY', 'IOC', 'ITC', 'JSWSTEEL',
       'KOTAKBANK', 'LT', 'M&M', 'MARUTI', 'NESTLEIND', 'NTPC', 'ONGC', 'POWERGRID', 'RELIANCE', 'SBILIFE', 'SBIN',
       'SHREECEM', 'SUNPHARMA', 'TATACONSUM', 'TATAMOTORS', 'TATASTEEL', 'TCS', 'TECHM', 'TITAN', 'ULTRACEMCO', 'UPL',
       'WIPRO']
MCX_FUT = ["MCX:NATURALGAS21DECFUT", "MCX:COTTON21DECFUT", "MCX:ALUMINIUM21DECFUT", "MCX:COPPER21DECFUT",
           "MCX:CPO21DECFUT", "MCX:LEAD21DECFUT", "MCX:ZINC21DECFUT", "MCX:NICKEL21DECFUT", "MCX:RUBBER21DECFUT",
           "MCX:MENTHAOIL21DECFUT", "MCX:GOLDGUINEA21DECFUT", "MCX:GOLDPETAL21DECFUT"]
