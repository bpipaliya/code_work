import pandas as pd
TimeFrame = 300
timenow = pd.Timestamp.now(tz='Asia/Kolkata')
t = timenow.minute / TimeFrame
print(t)