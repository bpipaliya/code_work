#!/usr/bin/env python
# coding: utf-8

# In[32]:





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


# In[31]:


redirect_uri = "https://127.0.0.1:5000/"
client_id='-100'
secret_key = ''
FY_ID = ""  # Your fyers ID
TOTP_KEY = ""  # TOTP secret is generated when we enable 2Factor TOTP from myaccount portal
PIN = "1234"  # User pin for fyers account



# In[33]:


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
#print(response)


access_token = response['access_token']

# Initialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path=os.getcwd())

# Make a request to get the user profile information
data = {"symbols":"NSE:SBIN-EQ"}
fyers.quotes(data)


# ## Place Order

# In[9]:


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

# In[10]:


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

# In[12]:


data = [{"id":'23092700210933'},{"id":'23092700210933'}]

cresponse = fyers.cancel_order(data=data)
cresponse


# ## EXIT position

# In[15]:


data = {'id':'NSE:SBIN-EQ-INTRADAY'}
fyers.exit_positions(data=data)


# In[14]:


fyers.positions()


# In[24]:


data = {
    "segment":[11],
    "side":[1],
    "productType":["INTRADAY"]
}

response = fyers.exit_positions(data=data)
response


# In[21]:


response


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# ## History

# In[34]:


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


# In[35]:


start = datetime.now() - timedelta(days=10)
start = int(start.timestamp())
start


# In[36]:


end = int(datetime.now().timestamp())
end


# In[37]:


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

# In[38]:


data = {
    "symbols":"NSE:SBIN-EQ,NSE:NIFTY23O1219600PE"
}

response = fyers.quotes(data=data)
response


# In[ ]:





# ## Market Depth

# In[43]:


data = {
    "symbol":"NSE:SBIN-EQ,NSE:NIFTY23O1219600PE",
    "ohlcv_flag":"1"
}

response = fyers.depth(data=data)
response


# In[ ]:




