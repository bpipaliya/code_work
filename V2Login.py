from fy_lib import *
credentials={
	"app_id"		: fyers_api2_id_BBP, # Ex: A1B2C3D4E5-678
	"app_secret"	: fyers_api2_secret_BBP,
	"fyers_id"		: fyers_user_id_BBP,
	"password"		: fyers_pwd_BBP,
	"panOrDob"		: "PAN",    # If you set PAN here then Enter your pan for 'pan_dob' , If you set DOB then set your Date of birth in DD-MM-YYYY format
	"pan_dob"		: fyers_two_fa_BBP,
	"redirect_uri"	: fyers_redirect_url  # Ex : http://localhost:1234/handler
}

from fyers_api import fyersModel
from fyers_api import accessToken
import requests
import re

session=accessToken.SessionModel(
	client_id	=credentials['app_id'],
	secret_key	=credentials['app_secret'],
	redirect_uri=credentials["redirect_uri"],
	response_type="code", 
	grant_type	='authorization_code',
	state		="abcdef"
	)
def get_auth_code(credentials):

	app_id , appType = credentials["app_id"].split("-")

	payload={

		"app_id"		:	app_id,
		"appType"		:	appType,
		"code_challenge":	"",
		"create_cookie"	:	False,
		"fyers_id"		:	credentials["fyers_id"],
		"nonce"			:	"",
		"pan_dob"		:	credentials["pan_dob"],
		"password"      :	credentials["password"],
		"redirect_uri"	:	credentials["redirect_uri"],
		"response_type"	:	"code",
		"scope"			:	"",
		"state"			:	"abcdef",   # You can change this value If needed

	}
	print(payload)
	
	session=accessToken.SessionModel(
		client_id=credentials['app_id'],
		secret_key=credentials['app_secret'],
		redirect_uri=credentials["redirect_uri"], 
		response_type="code", 
		grant_type='authorization_code',
		state="abcdef"
		)
	
	generate_auth_code_Url = session.generate_authcode()
	
	
	
	
	headers = {
		"accept": "*/*",
		"accept-language": "en-IN,en-US;q=0.9,en;q=0.8",
		"content-type": "application/json; charset=UTF-8",
		"sec-fetch-dest": "empty",
		"sec-fetch-mode": "cors",
		"sec-fetch-site": "same-origin",
		"referrer": generate_auth_code_Url
	}
	

	result = requests.post("https://api.fyers.in/api/v2/token",
							headers=headers, json=payload, allow_redirects=True)

	result_url = result.json()["Url"]
	
	auth_code = re.search(r'auth_code=(.*?)&', result_url, re.I)

	if auth_code:
		auth_code = auth_code.group(1)
		
		#print(auth_code)
		
		return auth_code
	return "error"

##################################

auth_code=get_auth_code(credentials)

print(auth_code)

session.set_token(auth_code)
access_token = session.generate_token()["access_token"]
f = open("token3.txt", "w")
f.write(access_token)
f.close()
print('access_token')
print(access_token)

### Done. Now you can use the access_token
