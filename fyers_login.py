import base64
import os
from datetime import datetime
from time import sleep
from urllib.parse import parse_qs, urlparse

import pyotp
import requests
from fyers_apiv3 import fyersModel

redirect_uri = "https://trade.fyers.in/api-login/redirect-uri/index.html"
client_id = 'E8KC42WAM1-100'
secret_key = 'MSRD7PRWLE'
FY_ID = "XB01059"  # Your fyers ID
TOTP_KEY = "4JAOSAZMBDYVS3IGONCPN7XKSHKIMJXK"
PIN = "1985"  # User pin for fyers account

session = fyersModel.SessionModel(client_id=client_id, secret_key=secret_key, redirect_uri=redirect_uri,
                                  response_type="code", grant_type="authorization_code")
urlToActivate = session.generate_authcode()
# print(f'URL to activateAPP: {urlToActivate}')


def getEncodedString(string):
    string = str(string)
    base64_bytes = base64.b64encode(string.encode("ascii"))
    return base64_bytes.decode("ascii")


URL_SEND_LOGIN_OTP = "https://api-t2.fyers.in/vagator/v2/send_login_otp_v2"
res = requests.post(url=URL_SEND_LOGIN_OTP, json={"fy_id": getEncodedString(FY_ID), "app_id": "2"}).json()


if datetime.now().second % 30 > 27: sleep(5)
URL_VERIFY_OTP = "https://api-t2.fyers.in/vagator/v2/verify_otp"
res2 = requests.post(url=URL_VERIFY_OTP,
                     json={"request_key": res["request_key"], "otp": pyotp.TOTP(TOTP_KEY).now()}).json()

ses = requests.Session()
URL_VERIFY_OTP2 = "https://api-t2.fyers.in/vagator/v2/verify_pin_v2"
payload2 = {"request_key": res2["request_key"], "identity_type": "pin", "identifier": getEncodedString(PIN)}
res3 = ses.post(url=URL_VERIFY_OTP2, json=payload2).json()
print(res3)

ses.headers.update({
    'authorization': f"Bearer {res3['data']['access_token']}"
})
TOKENURL = "https://api-t1.fyers.in/api/v3/token"
payload3 = {"fyers_id": FY_ID,
            "app_id": client_id[:-4],
            "redirect_uri": redirect_uri,
            "appType": "100", "code_challenge": "",
            "state": "None", "scope": "", "nonce": "", "response_type": "code", "create_cookie": True}

res3 = ses.post(url=TOKENURL, json=payload3).json()
url = res3['Url']
parsed = urlparse(url)
auth_code = parse_qs(parsed.query)['auth_code'][0]

grant_type = "authorization_code"
response_type = "code"
session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key,
    redirect_uri=redirect_uri,
    response_type=response_type,
    grant_type=grant_type
)
session.set_token(auth_code)
response = session.generate_token()
access_token = response['access_token']
fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path=os.getcwd())
data = {
    "symbol": "NSE:NIFTY50-INDEX",
    "strikecount": 10,
    "timestamp": ""
}
optRes = fyers.optionchain(data=data)

