#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[ ]:


pip install fyers-apiv3


# In[ ]:


from fyers_apiv3 import fyersModel


"""
In order to get started with Fyers API we would like you to do the following things first.
1. Checkout our API docs :   https://myapi.fyers.in/docsv3
2. Create an APP using our API dashboard :   https://myapi.fyers.in/dashboard/

Once you have created an APP you can start using the below SDK 
"""

#### Generate an authcode and then make a request to generate an accessToken (Login Flow)

                         ## app_secret key which you got after creating the app 
grant_type = "authorization_code"                  ## The grant_type always has to be "authorization_code"
response_type = "code"                             ## The response_type always has to be "code"
state = "sample"                                   ##  The state field here acts as a session manager. you will be sent with the state field after successfull generation of auth_code 


### Connect to the sessionModel object here with the required input parameters
appSession = fyersModel.SessionModel(client_id = client_id, redirect_uri = redirect_uri,response_type=response_type,state=state,secret_key=secret_key,grant_type=grant_type)

# ## Make  a request to generate_authcode object this will return a login url which you need to open in your browser from where you can get the generated auth_code 
generateTokenUrl = appSession.generate_authcode()
generateTokenUrl


# In[ ]:


redirect_uri = "https://127.0.0.1:5000/"
client_id='-100'
secret_key = ''
FY_ID = ""  # Your fyers ID
TOTP_KEY = ""  # TOTP secret is generated when we enable 2Factor TOTP from myaccount portal
PIN = "1234"  # User pin for fyers account



# In[ ]:


from fyers_apiv3 import fyersModel
from datetime import datetime, timedelta, date
from  time import sleep
import os
import pyotp
import requests
import json
import math
import pytz
from urllib.parse import parse_qs,urlparse
import warnings
import pandas as pd
pd.set_option('display.max_columns', None)
warnings.filterwarnings('ignore')

import base64
def getEncodedString(string):
    string = str(string)
    base64_bytes = base64.b64encode(string.encode("ascii"))
    return base64_bytes.decode("ascii")
  



URL_SEND_LOGIN_OTP="https://api-t2.fyers.in/vagator/v2/send_login_otp_v2"
res = requests.post(url=URL_SEND_LOGIN_OTP, json={"fy_id":getEncodedString(FY_ID),"app_id":"2"}).json()   
#print(res) 

if datetime.now().second % 30 > 27 : sleep(5)
URL_VERIFY_OTP="https://api-t2.fyers.in/vagator/v2/verify_otp"
res2 = requests.post(url=URL_VERIFY_OTP, json= {"request_key":res["request_key"],"otp":pyotp.TOTP(TOTP_KEY).now()}).json()  
#print(res2) 


ses = requests.Session()
URL_VERIFY_OTP2="https://api-t2.fyers.in/vagator/v2/verify_pin_v2"
payload2 = {"request_key": res2["request_key"],"identity_type":"pin","identifier":getEncodedString(PIN)}
res3 = ses.post(url=URL_VERIFY_OTP2, json= payload2).json()  
#print(res3) 


ses.headers.update({
    'authorization': f"Bearer {res3['data']['access_token']}"
})


TOKENURL="https://api-t1.fyers.in/api/v3/token"
payload3 = {"fyers_id":FY_ID,
           "app_id":client_id[:-4],
           "redirect_uri":redirect_uri,
           "appType":"100","code_challenge":"",
           "state":"None","scope":"","nonce":"","response_type":"code","create_cookie":True}

res3 = ses.post(url=TOKENURL, json= payload3).json()  
#print(res3)


url = res3['Url']
#print(url)
parsed = urlparse(url)
auth_code = parse_qs(parsed.query)['auth_code'][0]
auth_code


grant_type = "authorization_code" 

response_type = "code"  

session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key, 
    redirect_uri=redirect_uri, 
    response_type=response_type, 
    grant_type=grant_type
)

# Set the authorization code in the session object
session.set_token(auth_code)

# Generate the access token using the authorization code
response = session.generate_token()

# Print the response, which should contain the access token and other details
print(response)


access_token = response['access_token']

# Initialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path=os.getcwd())

# Make a request to get the user profile information
data = {"symbols":"NSE:SBIN-EQ"}
fyers.quotes(data)


# ## Place Order

# In[ ]:


data = {
    "symbol":"NSE:SBIN-EQ",
    "qty":1,
    "type":1,
    "side":1,
    "productType":"INTRADAY",
    "limitPrice":589,
    "stopPrice":0,
    "validity":"DAY",
    "disclosedQty":0,
    "offlineOrder":False,
}
response = fyers.place_order(data=data)
response


# ## Modify Order

# In[ ]:


orderId = "23092700210933"
data = {
    "id":orderId, 
    "type":1, 
    "limitPrice": 592, 
    "qty":2
}

mresponse = fyers.modify_order(data=data)
mresponse


# ## Cancel Order

# In[ ]:


data = [{"id":'23092700210933'},{"id":'23092700210933'}]

cresponse = fyers.cancel_order(data=data)
cresponse


# ## EXIT position

# In[ ]:


data = {'id':'NSE:SBIN-EQ-INTRADAY'}
fyers.exit_positions(data=data)


# In[ ]:


fyers.positions()


# In[ ]:


data = {
    "segment":[11],
    "side":[1],
    "productType":["INTRADAY"]
}

response = fyers.exit_positions(data=data)
response


# In[ ]:


response


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# ## History

# In[ ]:


from datetime import datetime, timedelta, date

data = {
    "symbol":"NSE:BANKNIFTY23OCTFUT",
    "resolution":"1",
    "date_format":"1",
    "range_from":str((datetime.now() - timedelta(days=10)).date()),
    "range_to":str(datetime.now().date()),
    "cont_flag":"1"
}

res = fyers.history(data=data)
data = pd.DataFrame(res['candles'],columns = ['date','open','high','low','close','volume'])
data['date'] = data['date'].apply(pd.Timestamp, unit='s', tzinfo=pytz.timezone('Asia/Kolkata'))
        
data = data.sort_values(by = 'date')
data


# In[ ]:


start = datetime.now() - timedelta(days=10)
start = int(start.timestamp())
start


# In[ ]:


end = int(datetime.now().timestamp())
end


# In[ ]:


data = {
    "symbol":"NSE:BANKNIFTY23OCTFUT",
    "resolution":"1",
    "date_format":"0",
    "range_from":start,
    "range_to":end,
    "cont_flag":"1"
}

res = fyers.history(data=data)
data = pd.DataFrame(res['candles'],columns = ['date','open','high','low','close','volume'])
data['date'] = data['date'].apply(pd.Timestamp, unit='s', tzinfo=pytz.timezone('Asia/Kolkata'))
        
data = data.sort_values(by = 'date')
data


# In[ ]:





# ##  Quotes

# In[ ]:


data = {
    "symbols":"NSE:SBIN-EQ,NSE:NIFTY23O1219600PE"
}

response = fyers.quotes(data=data)
response


# In[ ]:





# ## Market Depth

# In[ ]:


data = {
    "symbol":"NSE:SBIN-EQ,NSE:NIFTY23O1219600PE",
    "ohlcv_flag":"1"
}

response = fyers.depth(data=data)
response


# ## websocket
# 

# In[ ]:





# In[ ]:


from fyers_apiv3.FyersWebsocket import order_ws


def onTrade(message):
   
    print("Trade Response:", message)

def onOrder(message):
  
    print("Order Response:", message)

def onPosition(message):
 
    print("Position Response:", message)

def onGeneral(message):
   
    print("General Response:", message)
def onerror(message):
 
    print("Error:", message)


def onclose(message):
    print("Connection closed:", message)


def onopen():
    """
    Callback function to subscribe to data type and symbols upon WebSocket connection.

    """
    # Specify the data type and symbols you want to subscribe to
    # data_type = "OnOrders"
    # data_type = "OnTrades"
    # data_type = "OnPositions"
    # data_type = "OnGeneral"
    data_type = "OnOrders,OnTrades,OnPositions,OnGeneral"

    fyersOrderws.subscribe(data_type=data_type)

    # Keep the socket running to receive real-time data
    fyersOrderws.keep_running()


# Replace the sample access token with your actual access token obtained from Fyers
access_token = f'{client_id}:{access_token}'
# Create a FyersDataSocket instance with the provided parameters
fyersOrderws = order_ws.FyersOrderSocket(
    access_token=access_token,  # Your access token for authenticating with the Fyers API.
    write_to_file=False,        # A boolean flag indicating whether to write data to a log file or not.
    log_path="",                # The path to the log file if write_to_file is set to True (empty string means current directory).
    on_connect=onopen,          # Callback function to be executed upon successful WebSocket connection.
    on_close=onclose,           # Callback function to be executed when the WebSocket connection is closed.
    on_error=onerror,           # Callback function to handle any WebSocket errors that may occur.
    on_general=onGeneral,       # Callback function to handle general events from the WebSocket.
    on_orders=onOrder,          # Callback function to handle order-related events from the WebSocket.
    on_positions=onPosition,    # Callback function to handle position-related events from the WebSocket.
    on_trades=onTrade  , 
    reconnect  = True
    )

# Establish a connection to the Fyers WebSocket
fyersOrderws.connect()


# In[ ]:


fyersOrderws.is_connected()


# In[ ]:





# ## LTP websocket

# In[ ]:





# In[ ]:


from fyers_apiv3.FyersWebsocket import data_ws


def onmessage(message):
    """
    Callback function to handle incoming messages from the FyersDataSocket WebSocket.

    Parameters:
        message (dict): The received message from the WebSocket.

    """
    print("Response:", message)


def onerror(message):
    """
    Callback function to handle WebSocket errors.

    Parameters:
        message (dict): The error message received from the WebSocket.


    """
    print("Error:", message)


def onclose(message):
    """
    Callback function to handle WebSocket connection close events.
    """
    print("Connection closed:", message)


def onopen():
    """
    Callback function to subscribe to data type and symbols upon WebSocket connection.

    """
    # Specify the data type and symbols you want to subscribe to
    data_type = "SymbolUpdate"

    # Subscribe to the specified symbols and data type
    symbols = ['NSE:SBIN-EQ']
    fyersDataws.subscribe(symbols=symbols, data_type=data_type)

    # Keep the socket running to receive real-time data
    fyersDataws.keep_running()


# Replace the sample access token with your actual access token obtained from Fyers
access_token = f'{client_id}:{access_token}'

# Create a FyersDataSocket instance with the provided parameters
fyersDataws = data_ws.FyersDataSocket(
    access_token=access_token,       # Access token in the format "appid:accesstoken"
    log_path="",                     # Path to save logs. Leave empty to auto-create logs in the current directory.
    litemode=True,                  # Lite mode disabled. Set to True if you want a lite response.
    write_to_file=False,              # Save response in a log file instead of printing it.
    reconnect=True,                  # Enable auto-reconnection to WebSocket on disconnection.
    on_connect=onopen,               # Callback function to subscribe to data upon connection.
    on_close=onclose,                # Callback function to handle WebSocket connection close events.
    on_error=onerror,                # Callback function to handle WebSocket errors.
    on_message=onmessage             # Callback function to handle incoming messages from the WebSocket.
)

# Establish a connection to the Fyers WebSocket
fyersDataws.connect()

 


# In[ ]:


{'ltp': 590.25, 'vol_traded_today': 3009973, 'last_traded_time': 1697093444,
 'exch_feed_time': 1697093444, 'bid_size': 149, 'ask_size': 111, 'bid_price': 590.1, 
 'ask_price': 590.25, 'last_traded_qty': 78, 'tot_buy_qty': 798445, 'tot_sell_qty': 1961932,
 'avg_trade_price': 591.33, 'low_price': 589.55, 'high_price': 593.0, 'lower_ckt': 0, 'upper_ckt': 0, 
 'open_price': 590.8, 'prev_close_price': 588.35, 'type': 'sf', 'symbol': 'NSE:SBIN-EQ', 'ch': 1.9, 'chp': 0.3229}


# In[ ]:


fyersDataws.is_connected()


# In[ ]:


fyersDataws.close_connection()

