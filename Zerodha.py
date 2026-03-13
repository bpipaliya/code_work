import credentials
import logging
from kiteconnect import KiteConnect
logging.basicConfig(level=logging.DEBUG)
kite = KiteConnect(api_key=credentials.zerodha_api_key)

data = kite.generate_session("request_token_here", api_secret="your_secret")
kite.set_access_token(data["access_token"])

from kiteconnect import WebSocket
api_key = 'your_api_key'
public_token = 'your_public_token'
client_id = 'your_id'
# here i have added nifty 50 indices and then MCX GOLD contract
tokens = [53372167, 256265]

pa = WebSocket(api_key, public_token, client_id)
"After login flow and tokens define tick and tell them to print and then a flow for webscoket need to subscribe and said about mode whether you want to set in FULL, LTP and QUOTE mode and assign them with callbacks and then say them to connect."


def on_tick(tick, wbskt):
    print(tick)


def on_connect(wbskt):
    wbskt.subscribe(tokens)
    wbskt.set_mode(wbskt.MODE_FULL, tokens)


pa.on_tick = on_tick
pa.on_connect = on_connect

pa.connect()
"Note: it Supports in Python 3.0 Client best for Full Mode Code please Visit Below for Code Input:"

from kiteconnect import WebSocket

api_key = 'your_api_key'
public_token = 'your_public_token'
client_id = 'your_id'
# here i have added nifty 50 indices and then MCX GOLD contract
tokens = [53372167, 256265]

pa = WebSocket(api_key, public_token, client_id)


def on_tick(tick, wbskt):
    print(tick)


def on_connect(wbskt):
    wbskt.subscribe(tokens)
    # set the mode as you wish for market watch
    wbskt.set_mode(wbskt.MODE_FULL, tokens)


pa.on_tick = on_tick
pa.on_connect = on_connect

pa.connect()