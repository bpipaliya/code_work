import os
import sys
from urllib.parse import urlparse, parse_qs
from fyers_api import fyersModel
from fyers_api import accessToken
import requests

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
from fy_lib import *

username = fyers_user_id_BBP    # fyers_id
password = fyers_pwd_BBP
pin = 3185    # your integer pin
client_id = fyers_api2_id_BBP    # '##########-$$$'
secret_key = fyers_api2_secret_BBP
redirect_uri = fyers_redirect_url

app_id = client_id[:-4]    # '##########'

# Auth functions
def read_file():
    with open("tokenf.txt", "r") as f:
        token = f.read()
    return token


def write_file(token):
    with open('tokenf.txt', 'w') as f:
        f.write(token)


def setup():
    session = accessToken.SessionModel(
        client_id=client_id,
        redirect_uri=redirect_uri,
        response_type='code',
        scope=None,
        state='abcd',
        nonce=None,
        secret_key=secret_key,
        grant_type='authorization_code'
    );

    #session = accessToken.SessionModel(client_id, secret_key, redirect_uri,
    #                                   response_type='code', grant_type='authorization_code')

    s = requests.Session()

    data1 = f'{{"fy_id":"{username}","password":"{password}","app_id":"2","imei":"","recaptcha_token":""}}'
    r1 = s.post('https://api.fyers.in/vagator/v1/login', data=data1)
    request_key = r1.json()["request_key"]

    data2 = f'{{"request_key":"{request_key}","identity_type":"pin","identifier":"{pin}","recaptcha_token":""}}'
    r2 = s.post('https://api.fyers.in/vagator/v1/verify_pin', data=data2)

    headers = {
        'authorization': f"Bearer {r2.json()['data']['access_token']}",
        'content-type': 'application/json; charset=UTF-8'
    }

    data3 = f'{{"fyers_id":"{username}","app_id":"{app_id}","redirect_uri":"{redirect_uri}","appType":"100","code_challenge":"","state":"abcdefg","scope":"","nonce":"","response_type":"code","create_cookie":true}}'

    r3 = s.post('https://api.fyers.in/api/v2/token', headers=headers, data=data3)

    parsed = urlparse(r3.json()['Url'])
    auth_code = parse_qs(parsed.query)['auth_code'][0]
    session.set_token(auth_code)
    response = session.generate_token()
    token = response["access_token"]
    write_file(token)
    print('Got the access token!!!')
    fyers = fyersModel.FyersModel(is_async=False, client_id=client_id, token=token, log_path=os.getcwd())

    print(fyers.get_profile())


def check():
    try:
        token = read_file()
    except FileNotFoundError:
        print('Getting the access token!')
        setup()
        return {'message': 'got access token!'}

    fyers = fyersModel.FyersModel(client_id=client_id, token=token, log_path=os.getcwd())
    response = fyers.get_profile()
    if 'error' in response['s'] or 'error' in response['message'] or 'expired' in response['message']:
        print('Getting a access token!')
        setup()
    else:
        print('You already have a access token!')
        print(response)


app = Chalice(app_name='hw')

@app.route('/')
def index():
    check()
    return {'Hare': 'Srinivasa'}

@app.route('/webhook', methods=['POST'])
def webhook():
    check()
    request = app.current_request
    webhook_msg = request.json_body
    print(request.json_body)
    return {
        'MESSAGE': 'TV alert!',
        'webhook_msg': webhook_msg
    }