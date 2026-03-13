import pandas as pd
import credentials
from datetime import datetime

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
data = pd.read_csv("http://public.fyers.in/sym_details/NSE_FO.csv", names=[*range(0, 14, 1)])


data = data.drop([0, 4, 5, 6, 7, 12, 13], axis=1)
column = ["Symbol_Details", "Exchange_Instrument_type", "Minimum_lot_size",
          "Expiry_date", "Symbol_ticker", "Exchange", "Segment"]
data.columns = column
data['Expiry_date'] = (pd.to_datetime(data['Expiry_date'], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
data['Expiry_date'] = pd.to_datetime(data['Expiry_date']).dt.date
# data.to_csv("Fyers_symlol.csv")
# data = pd.read_csv("Fyers_symlol_MCX.csv")
# # data = data[data['Exchange'] == 10]
# data = data[data['Exchange_Instrument_type'] == 30] # 13 FOR NSE FUTURE
# print(data)
# data = data[data['Expiry_date'] == 1635431400] # change Expiry_date as per near Expiry_date
#
# data = data[["Symbol_ticker", "Minimum_lot_size"]]
# data.set_index(data["Symbol_ticker"], inplace=True)
# data = data.drop(["Symbol_ticker"], axis=1)
# data = data.to_dict()

print(data)
# symbols = ["NSE:ADANIPORTS-EQ"]
# Expiry_date = "21OCT"
# for symbol in symbols:
#     fut_symbol = symbol [ 0:-3 ] + Expiry_date + "FUT"
#     # print(fut_symbol)
#     for Symbol_ticker in data:
#         if Symbol_ticker == str(fut_symbol):
#             print(Symbol_ticker)





# data["Expiry_date"] = (pd.to_datetime(data["Expiry_date"], unit='s').dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata'))
# data["Expiry_date"] = pd.to_datetime(data["Expiry_date"]).dt.strftime('%Y-%m-%d')
#
# data["Exchange"]= data["Exchange"].replace(10, "NSE")
# data["Exchange"]= data["Exchange"].replace(11, "MCX")
# data["Segment"]= data["Segment"].replace(10, "Capital_Market")
# data["Segment"]= data["Segment"].replace(11, "Equity_Derivatives")
# data["Segment"]= data["Segment"].replace(12, "Currency_Derivatives")
# data["Segment"]= data["Segment"].replace(13, "Commodity_Derivatives")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(0, "EQ")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(1, "PREFSHARES")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(2, "DEBENTURES")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(3, "WARRANTS")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(4, "MISC")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(10, "INDEX")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(11, "FUTIDX")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(12, "FUTIVX")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(13, "FUTSTK")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(14, "OPTIDX")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(15, "OPTSTK")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(16, "FUTCUR")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(17, "FUTIRT")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(18, "FUTIRC")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(19, "OPTCUR")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(20, "UNDCUR")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(21, "UNDIRC")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(22, "UNDIRT")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(23, "UNDIRD")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(24, "INDEX_CD")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(25, "FUTIRD")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(30, "FUTCOM")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(31, "OPTFUT")
# data["Exchange_Instrument_type"]= data["Exchange_Instrument_type"].replace(32, "OPTCOM")
#
# data.to_csv("fyers_symbol.csv")
