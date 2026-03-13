import pandas as pd
import credentials
import requests

url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
d = requests.get(url).json()
token_df = pd.DataFrame.from_dict(d)
token_df['expiry'] = pd.to_datetime(token_df['expiry'])
token_df = token_df.astype({'strike': float})
token_df.to_csv('angle_token.csv', header=True, index=False)
credentials.TOKEN_MAP = token_df
print(credentials.TOKEN_MAP)
