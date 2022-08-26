import psycopg2
import psycopg2.extras
import os
import requests
import time
import json

from helpers import get_stock_info

#Progres DataBase URL
if not os.environ.get('DATABASE_URL'):
    raise RuntimeError("DATABASE_URL NOT SET")
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#Get api key
if not os.environ.get('IEX_API_KEY'):
    raise RuntimeError('IEX_API_KEY NOT SET')
IEX_API_KEY = os.environ['IEX_API_KEY']
UPDATE_INTERVAL = 86400

def getone():
    row = cur.fetchone()
    if row is None:
        return None
    return dict(row)

def getall():
    data = []
    rows = cur.fetchall()
    if not rows:
        return None
    for row in rows:
        data.append(dict(row))
    return data

#Returns account balance
def getBalance(id):
    cur.execute("SELECT balance FROM users WHERE id=%s",(id,))
    balance = getone()["balance"]
    return f"${balance:,.2f}"

def oneYearMonthPrices(symbol):
    cur.execute("SELECT * FROM historical_prices WHERE symbol=%s", (symbol,))
    res = getone()
    if (res is None) or (int(time.time()) - res["epoch"] > UPDATE_INTERVAL):
        response = requests.get(f"https://cloud.iexapis.com/beta/stock/{symbol}/batch?token={IEX_API_KEY}&types=chart,quote&range=1y")
        stock_data_year = response.json()
        year = response.text
        response = requests.get(f"https://cloud.iexapis.com/beta/stock/{symbol}/batch?token={IEX_API_KEY}&types=chart,quote&range=1m")
        stock_data_month = response.json()
        month = response.text
        # print(type(stock_data_month))
        epoch_time = int(time.time())
        cur.execute("INSERT INTO historical_prices(symbol,onemonth,oneyear,epoch) VALUES (%s,%s,%s,%s);", (symbol, month, year, epoch_time))
        cur.execute("COMMIT;")
    else:
        stock_data_year = json.loads(res["oneyear"])
        stock_data_month = json.loads(res["onemonth"])

    return {
        "oneYear": stock_data_year,
        "oneMonth": stock_data_month
    }

def isBookmark(id, symbol):
    cur.execute("SELECT * FROM watchlist WHERE id=%s AND symbol=%s;", (id, symbol))
    res = getone()
    if res is None:
        return False
    return True

def getBookmark(id):
    cur.execute("SELECT symbol FROM watchlist WHERE id=%s;", (id,))
    res = getall()
    if res is None:
        return False
    bookmarks = []
    for row in res:
        bookmarks.append(get_stock_info(row["symbol"]))
    return bookmarks