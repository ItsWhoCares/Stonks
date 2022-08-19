import requests
import datetime
import pyEX as p
import os
import psycopg2
c = p.Client(api_token='pk_13bea402dd284dd994c2a87b076d4d9f') 

if not os.environ.get('DATABASE_URL'):
    raise RuntimeError("DATABASE_URL NOT SET")
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()


def news(symbol):
    articles = c.news(symbol)[:3]
    return [
        {
            "Date": datetime.datetime.fromtimestamp(articles[0]["datetime"]/1000).strftime("%B %d"),
            "ImageUrl": articles[0]["image"],
            "Headline": articles[0]["headline"],
            "Summary": articles[0]["summary"][0:120],
            "Url": articles[0]["url"]
        },
        {
            "Date": datetime.datetime.fromtimestamp(articles[1]["datetime"]/1000).strftime("%B %d"),
            "ImageUrl": articles[1]["image"],
            "Headline": articles[1]["headline"],
            "Summary": articles[1]["summary"][0:120],
            "Url": articles[1]["url"]
        },
        {
            "Date": datetime.datetime.fromtimestamp(articles[2]["datetime"]/1000).strftime("%B %d"),
            "ImageUrl": articles[2]["image"],
            "Headline": articles[2]["headline"],
            "Summary": articles[2]["summary"][0:120],
            "Url": articles[2]["url"]
        }
    ]


sym = "AAPL"
# art = news(sym)

cur.execute("SELECT * FROM news WHERE Symbol=%s;", (sym,))
row = cur.fetchall()
print(row)
# cur.execute("INSERT INTO news VALUES(%s,%s,%s,%s,%s,%s);",(sym, art[0]["Headline"], art[0]["ImageUrl"], art[0]["Summary"], art[0]["Url"], art[0]["Date"],))
# cur.execute("COMMIT;")



# symbol = 'BBBY'
# # my_time = datetime.datetime.fromtimestamp(1660647693000/1000).strftime("%B %d")
# # print(my_time)
# # api_key = 'SAOS0Y8B63XM4DPK'
# # url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={api_key}"
# # response = requests.get(url)

# # chart = response.json()
# # labels = []
# # data = []

# # for label in chart["Time Series (1min)"]:
# #     data.append(round(float(chart["Time Series (1min)"][label]["4. close"]),2))

# # print(data)

# print(c.quote(symbol))