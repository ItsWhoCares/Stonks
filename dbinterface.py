import psycopg2
import psycopg2.extras
import os
import requests
import time
import json

from helpers import get_stock_info, get_stock_price

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

def getUserName(id):
    cur.execute("SELECT username FROM users WHERE id=%s", (id,))
    res = getone()["username"]
    return res


#Returns account balance formated
def getBalancef(id):
    cur.execute("SELECT balance FROM users WHERE id=%s",(id,))
    balance = getone()["balance"]
    return f"${balance:,.2f}"

#Returns account balance
def getBalance(id):
    cur.execute("SELECT balance FROM users WHERE id=%s",(id,))
    balance = getone()["balance"]
    return float(balance)

def oneYearMonthPrices(symbol):
    cur.execute("SELECT * FROM historical_prices WHERE symbol=%s", (symbol,))
    res = getone()
    if (res is None) or ((int(time.time()) - res["epoch"]) > UPDATE_INTERVAL):
        # print("API called")
        response = requests.get(f"https://cloud.iexapis.com/beta/stock/{symbol}/batch?token={IEX_API_KEY}&types=chart,quote&range=1y")
        stock_data_year = response.json()
        year = response.text
        response = requests.get(f"https://cloud.iexapis.com/beta/stock/{symbol}/batch?token={IEX_API_KEY}&types=chart,quote&range=1m")
        stock_data_month = response.json()
        month = response.text
        # print(type(stock_data_month))
        epoch_time = int(time.time())
        if res is not None and ((int(time.time()) - res["epoch"]) > UPDATE_INTERVAL):
            # print("deleted old record")
            cur.execute("DELETE FROM historical_prices WHERE symbol=%s", (symbol,))
        cur.execute("INSERT INTO historical_prices(symbol,onemonth,oneyear,epoch) VALUES (%s,%s,%s,%s);", (symbol, month, year, epoch_time))
        cur.execute("COMMIT;")
        
    else:
        # print("DB used")
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

#Can user afford to buy
def canBuy(amount, id):
    cur.execute("SELECT balance FROM users where id=%s", (id,))
    balance = getone()["balance"]
    return balance >= amount

#Does user own that stock
def canSell(uid, symbol, tid):
    cur.execute("SELECT * FROM transactions WHERE uid=%s and tid=%s and type=%s", (uid, tid, "B"))
    res = getone()
    if res is None:
        return False
    cur.execute("SELECT * FROM portfolio WHERE uid=%s and tid=%s and symbol=%s", (uid, tid, symbol))
    res = getone()
    if res is None:
        return False
    return True


def makeBuyTransaction(uid, symbol, buyp, buyq):
    bill = round(buyp * float(buyq), 4)
    Time = int(time.time())
    cur.execute("INSERT INTO transactions(uid, type, symbol, buyp, buyq, bill, etime) VALUES (%s, %s, %s, %s, %s, %s, %s);",(uid, "B", symbol, buyp, buyq, bill, Time))
    cur.execute("COMMIT;")
    cur.execute("SELECT tid FROM transactions WHERE uid=%s and etime=%s", (uid, Time))
    tid = getone()["tid"]
    addToPortfolio(uid, tid, symbol, buyp, buyq, bill, Time)
    return True


def makeSellTransaction(uid, tid, sellp):
    cur.execute("SELECT * FROM transactions WHERE uid=%s and tid=%s", (uid, tid))
    res = getone()
    bill = round(sellp * float(res["buyq"]), 4)
    Time = int(time.time())
    cur.execute("INSERT INTO transactions(uid, type, symbol, sellp, sellq, bill, etime) VALUES (%s, %s, %s, %s, %s, %s, %s);",(uid, "S", res["symbol"], sellp, res["buyq"], bill, Time))
    cur.execute("COMMIT;")
    removeFromPortfolio(uid, tid, bill)
    return True

def addToPortfolio(uid, tid, symbol, buyp, buyq, value, Time):
    balance = getBalance(uid)
    newBalance = round(balance - value, 4)
    cur.execute("UPDATE users SET balance=%s WHERE id=%s", (newBalance, uid))
    cur.execute("INSERT INTO portfolio(uid, tid, symbol, quantity, buyp, value, etime) VALUES(%s, %s, %s, %s, %s, %s, %s)", (uid, tid, symbol, buyq, buyp, value, Time))
    cur.execute("COMMIT;")

def removeFromPortfolio(uid, tid, bill):
    balance = getBalance(uid)
    newBalance = round(balance + bill, 4)
    cur.execute("UPDATE users SET balance=%s WHERE id=%s", (newBalance, uid))
    cur.execute("DELETE FROM portfolio WHERE uid=%s and tid=%s", (uid, tid))
    cur.execute("COMMIT;")


def getPortfolio(uid):
    cur.execute("SELECT * FROM portfolio WHERE uid=%s", (uid,))
    res = getall()
    if res is None:
        return False
    stocks = []
    for stock in res:
        stockPrice = get_stock_price(stock["symbol"], 4)
        currentValue = round(float(stock["quantity"]) * stockPrice, 2)
        change = currentValue - float(stock["value"])
        if change < 0:
            change = change * -1
        change = f"${change:,.2f}"
        stocks.append({
            "Symbol": stock["symbol"].upper(),
            "Quantity": stock["quantity"],
            "ChangeSign": currentValue >= stock["value"],
            "Change": change,
            "CurrentValue": currentValue,
            "tid": stock["tid"]
        })
    return stocks


def credit(id, amount):
    cur.execute("SELECT balance FROM users WHERE id=%s", (id,))
    balance = getone()["balance"]
    if balance >= 100000:
        return False
    newbalance = balance + amount
    cur.execute("UPDATE users SET balance=%s WHERE id=%s", (newbalance, id))
    cur.execute("COMMIT;")
    return True

#print the names of all the tables in the database
def printTables():
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    res = getall()
    for row in res:
        print(row["table_name"])
        
