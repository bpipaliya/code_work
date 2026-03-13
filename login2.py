import base64
import os
import sys
from datetime import datetime
from time import sleep
from urllib.parse import urlparse, parse_qs

import pyotp
from fyers_apiv3 import fyersModel
import requests

fyers_user_id_BBP = 'XB01059'
fyers_totp_key_BBP = "4JAOSAZMBDYVS3IGONCPN7XKSHKIMJXK"
fyers_api_id_BBP = 'E8KC42WAM1-100'
fyers_api_secret_BBP = 'MSRD7PRWLE'
fyers_pin_BBP = "3185"
fyers_redirect_uri_BBP = "https://trade.fyers.in/api-login/redirect-uri/index.html"


def read_file():
    with open("access_token2_BBP.txt", "r") as f:
        token = f.read()
    return token


def write_file(token):
    with open('access_token2_BBP.txt', 'w') as f:
        f.write(token)

def getEncodedString(string):
    string = str(string)
    base64_bytes = base64.b64encode(string.encode("ascii"))
    return base64_bytes.decode("ascii")


def setup():
    URL_SEND_LOGIN_OTP = "https://api-t2.fyers.in/vagator/v2/send_login_otp_v2"
    res = requests.post(url=URL_SEND_LOGIN_OTP, json={"fy_id": getEncodedString(fyers_user_id_BBP), "app_id": "2"}).json()

    if datetime.now().second % 30 > 27 : sleep(5)
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
    token = response["access_token"]
    write_file(token)
    print('Got the access token!!!')
    fyers = fyersModel.FyersModel(client_id=fyers_user_id_BBP, is_async=False, token=token, log_path=os.getcwd())
    print(fyers.get_profile())


def check():
    try:
        token = read_file()
    except FileNotFoundError:
        print('Getting the access token!')
        setup()
        sys.exit()
    fyers = fyersModel.FyersModel(client_id=fyers_user_id_BBP, is_async=False,  token=token, log_path=os.getcwd())
    response = fyers.get_profile()
    print(response)
    if 'error' in response['s'] or 'error' in response['message'] or 'expired' in response['message']:
        print('Getting a access token!')
        setup()
    else:
        print('You already have a access token!')
        print(response)


if __name__ == '__main__':
    check()
