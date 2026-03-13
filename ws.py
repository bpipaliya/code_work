from fyers_api.websocket import ws
from Trading_Setup import credentials

Access_token = credentials.api_id + ":" + open("Trading_Setup/access_token_BBP.txt", "r").read()


# def OrderUpdate(self):
#     print("OrderUpdate " + str(self.response))
# data_type = "orderUpdate"
# ws.FyersSocket.websocket_data = OrderUpdate
# fyersSocket = ws.FyersSocket(access_token=Access_token, data_type=data_type)
# fyersSocket.subscribe()



def SymbolData(self):
    print("SymbolData " + str(self.response))
Data_type = "symbolData"
Symbol = ["NSE:SBIN-EQ"]
ws.FyersSocket.websocket_data = SymbolData
fyersSocket = ws.FyersSocket(access_token=Access_token, data_type=Data_type, symbol=Symbol)
fyersSocket.subscribe()

