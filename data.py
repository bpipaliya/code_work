import fy_lib

data = fy_lib.oc_data["OC_1"]["Symbol"]
for symbol in fy_lib.oc_data:
    data = {
        "symbol": fy_lib.oc_data[symbol]["Symbol"],
        # "NSE:NIFTY50-INDEX" "NSE:NIFTYBANK-INDEX" "BSE:SENSEX-INDEX" "BSE:BANKEX-INDEX" "NSE:FINNIFTY-INDEX"
        "strikecount": 2,
        "timestamp": ""
    }
    # optRes = fyers.optionchain(data=data)
    print(data)

# print(data)