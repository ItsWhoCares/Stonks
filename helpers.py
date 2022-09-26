import os
import requests
import urllib.parse
import pyEX as p
import datetime

from numerize import numerize
from flask import redirect, render_template, request, session
from functools import wraps


if not os.environ.get('IEX_API_KEY'):
    raise RuntimeError('IEX_API_KEY NOT SET')
IEX_API_KEY = os.environ['IEX_API_KEY']

if not os.environ.get('NEWS_API_KEY'):
    raise RuntimeError('NEWS_API_KEY NOT SET')
NEWS_API_KEY = os.environ['NEWS_API_KEY']


api_one = p.Client(api_token='sk_bdf4a921914e4977b60e9b40fc9f1b3e') #whocares
api_two = p.Client(api_token='pk_13bea402dd284dd994c2a87b076d4d9f')#cities

news_key = p.Client(api_token=NEWS_API_KEY)
api_key = p.Client(api_token=IEX_API_KEY)

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# def lookup(symbol):
#     """Look up quote for symbol."""

#     # Contact API
#     try:
#         api_key = pk_a8218b82cc0b4e929be5cb4a3795e82c
#         url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
#         response = requests.get(url)
#         response.raise_for_status()
#     except requests.RequestException:
#         return None

#     # Parse response
#     try:
#         quote = response.json()
#         return {
#             "name": quote["companyName"],
#             "price": float(quote["latestPrice"]),
#             "symbol": quote["symbol"]
#         }
#     except (KeyError, TypeError, ValueError):
#         return None


def Most_active():
    ma = api_key.list()[:9]
    if not ma:
        return None
    return [
        {
            "symbol": ma[0]["symbol"],
            "companyName": ma[0]["companyName"],
            "latestPrice": round(ma[0]["latestPrice"], 2),
            "changePercent": round(ma[0]["changePercent"] * 100, 2)
        },
        {
            "symbol": ma[1]["symbol"],
            "companyName": ma[1]["companyName"],
            "latestPrice": round(ma[1]["latestPrice"], 2),
            "changePercent": round(ma[1]["changePercent"] * 100, 2)
        },
        {
            "symbol": ma[2]["symbol"],
            "companyName": ma[2]["companyName"],
            "latestPrice": round(ma[2]["latestPrice"], 2),
            "changePercent": round(ma[2]["changePercent"] * 100, 2)
        },
        {
            "symbol": ma[3]["symbol"],
            "companyName": ma[3]["companyName"],
            "latestPrice": round(ma[3]["latestPrice"], 2),
            "changePercent": round(ma[3]["changePercent"] * 100, 2)
        },
        {
            "symbol": ma[4]["symbol"],
            "companyName": ma[4]["companyName"],
            "latestPrice": round(ma[4]["latestPrice"], 2),
            "changePercent": round(ma[4]["changePercent"] * 100, 2)
        },
        {
            "symbol": ma[5]["symbol"],
            "companyName": ma[5]["companyName"],
            "latestPrice": round(ma[5]["latestPrice"], 2),
            "changePercent": round(ma[5]["changePercent"] * 100, 2)
        },
        {
            "symbol": ma[6]["symbol"],
            "companyName": ma[6]["companyName"],
            "latestPrice": round(ma[6]["latestPrice"], 2),
            "changePercent": round(ma[6]["changePercent"] * 100, 2)
        },
        {
            "symbol": ma[7]["symbol"],
            "companyName": ma[7]["companyName"],
            "latestPrice": round(ma[7]["latestPrice"], 2),
            "changePercent": round(ma[7]["changePercent"] * 100, 2)
        },
        {
            "symbol": ma[8]["symbol"],
            "companyName": ma[8]["companyName"],
            "latestPrice": round(ma[8]["latestPrice"], 2),
            "changePercent": round(ma[8]["changePercent"] * 100, 2)
        }
    ]



def is_market_open():
    status = api_key.quote('aapl')
    return status["isUSMarketOpen"]

def get_stock_price(symbol,n):
    return round(api_key.quote(symbol)["latestPrice"], n)

def get_stock_info(symbol):
    stock_info = api_key.quote(symbol)
    if stock_info["latestVolume"] is None:
        stock_info["latestVolume"] = "---"
    else:
        stock_info["latestVolume"] = "{:,}".format(stock_info["latestVolume"])
    return {
        "Symbol": symbol,
        "CompanyName": stock_info["companyName"],
        "Market Cap": numerize.numerize(stock_info["marketCap"]),
        "PE Ratio (TTM)": stock_info["peRatio"],
        "52 week High": stock_info["week52High"],
        "52 week Low": stock_info["week52Low"],
        "YTD Change": round(stock_info["ytdChange"] * 100, 2),
        "Volume": stock_info["latestVolume"],
        "LatestPrice": round(stock_info["latestPrice"], 2),
        "Change": stock_info["change"],
        "ChangePercent": round(stock_info["changePercent"] * 100, 2)
    }

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def news(symbol):
    try:
        articles = news_key.news(symbol)[:3]
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

    except:
        return None
def getOneDayChart(symbol):
    labels = []
    data = []
    chart = {
        "labels":[],
        "data":[]
    }
    url = f"https://cloud.iexapis.com/stable/stock/{symbol}/intraday-prices/chartIEXOnly=true/?token={IEX_API_KEY}"
    response = requests.get(url).json()
    if not response:
        api_key = 'SAOS0Y8B63XM4DPK'
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={api_key}"
        response = requests.get(url).json()["Time Series (1min)"]
        for label in response["Time Series (1min)"]:
            labels.append(label.split(" ")[1][:5])
    
        for label in response["Time Series (1min)"]:
            data.append(round(float(response["Time Series (1min)"][label]["4. close"]),2))

        for label in labels:
            chart["labels"].append(label)

        for dat in data:
            chart["data"].append(dat)
        chart["labels"].reverse()
        chart["data"].reverse()
        return chart

    for ever_minute in response:
        if ever_minute["close"] is not None:
            labels.append(ever_minute["minute"])
            data.append(ever_minute["close"])
    chart["labels"] = labels
    chart["data"] = data
    return chart
    




def getTopGainers():
    url = f"https://cloud.iexapis.com/stable/stock/market/list/gainers/?token={IEX_API_KEY}"
    res = requests.get(url)
    stocks = res.json()
    topGainers = []
    for stock in stocks:
        if stock is not None and stock["change"] is not None:
            topGainers.append({
            "Symbol": stock["symbol"],
            "CompanyName": stock["companyName"],
            "LatestPrice": round(stock["latestPrice"],2),
            "Change": round(stock["change"],2),
            "52 Week High": round(stock["week52High"],2),
            "52 Week Low": round(stock["week52Low"],2)
        })

    return topGainers[:7]

def getTopLosers():
    url = f"https://cloud.iexapis.com/stable/stock/market/list/losers/?token={IEX_API_KEY}"
    res = requests.get(url)
    stocks = res.json()
    topLosers = []
    for stock in stocks:
        if stock is not None and stock["change"] is not None:
            topLosers.append({
            "Symbol": stock["symbol"],
            "CompanyName": stock["companyName"],
            "LatestPrice": round(stock["latestPrice"],2),
            "Change": round(stock["change"],2),
            "52 Week High": round(stock["week52High"],2),
            "52 Week Low": round(stock["week52Low"],2)
        })

    return topLosers[:7]



def getTopVolume():
    url = f"https://cloud.iexapis.com/stable/stock/market/list/iexvolume/?token={IEX_API_KEY}"
    res = requests.get(url)
    stocks = res.json()
    topVolume = []
    for stock in stocks:
        if stock is not None and stock["change"] is not None:
            topVolume.append({
            "Symbol": stock["symbol"],
            "CompanyName": stock["companyName"],
            "LatestPrice": round(stock["latestPrice"],2),
            "Change": round(stock["change"],2),
            "52 Week High": round(stock["week52High"],2),
            "52 Week Low": round(stock["week52Low"],2)
        })

    return topVolume[:7]