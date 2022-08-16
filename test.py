import requests
import datetime
import pyEX as p
c = p.Client(api_token='sk_bdf4a921914e4977b60e9b40fc9f1b3e') 


symbol = 'AMC'
my_time = datetime.datetime.fromtimestamp(1660647693000/1000).strftime("%B %d")
print(my_time)
# api_key = 'SAOS0Y8B63XM4DPK'
# url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={api_key}"
# response = requests.get(url)

# chart = response.json()
# labels = []
# data = []

# for label in chart["Time Series (1min)"]:
#     data.append(round(float(chart["Time Series (1min)"][label]["4. close"]),2))

# print(data)