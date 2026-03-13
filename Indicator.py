"""
df['ATR_14'] = talib.ATR(df.high, df.low, df.close, timeperiod=14)
df["MA_10"] = talib.MA(df.close, timeperiod=10)
df["SMA_20"] = talib.MA(df.close, timeperiod=20)
df["RSI_14"] = talib.RSI(df.close, timeperiod=14)
df["BBU"], df["BBM"], df["BBL"] = talib.BBANDS(df.close, timeperiod=20, nbdevup=2, nbdevdn=2)
df["MACD"], df["MACD_S"], df["MACD_H"] = talib.MACD(df.close, fastperiod=12, slowperiod=26, signalperiod=9)
df['MFI_14'] = talib.MFI(df.high, df.low, df.close, df.volume, timeperiod=14)
df['AROON_D'], df['ARRON_U'] = talib.AROON(df.high, df.low, timeperiod=14)
df['ARRON_OSC'] = talib.AROONOSC(df.high, df.low, timeperiod=14)
df['MOM'] = talib.MOM(df.close, timeperiod=10)
df["volatility"] = round((df["high"]-df["low"]) * 100 / df["open"], 2)

df['ST'] = pdta.supertrend(df['High'], df['Low'], df['Close'], 7, 3)
df['CMF_20'] = pdta.cmf(high=df.high, low=df.low, close=df.close, volume=df.volume)
df['VWAP'] = pdta.vwap(high=df.high, low=df.low, close=df.close, volume=df.volume, anchor=None, offset=None)
df['ST'] = pdta.supertrend(high=df.high, low=df.low, close=df.close, period=7, multiplier=3)['SUPERT_7_3.0']




now = pd.Timestamp.now(tz='Asia/Kolkata')





TA-lib
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzvf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure --prefix=/usr
make
make install
pip install Ta-Lib



SELENIUM
!pip install selenium
!apt-get update # to update ubuntu to correctly run apt install
!apt install chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin
import sys
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
wd = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
wd.get("https://www.webite-url.com")
"""

async def checkSignal():
	tasks = []
	for symbol in SYMBOL_LIST:
		tasks.append(getHistoricalData(symbol))
		results = await asyncio.gather(*tasks)

