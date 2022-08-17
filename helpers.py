import os
import requests
import urllib.parse
import pyEX as p
import datetime

from numerize import numerize
from flask import redirect, render_template, request, session
from functools import wraps


c = p.Client(api_token='sk_bdf4a921914e4977b60e9b40fc9f1b3e') 

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


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = pk_a8218b82cc0b4e929be5cb4a3795e82c
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None

def Most_active():
    ma = c.list()[:9]
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
    status = c.quote('aapl')
    return status["isUSMarketOpen"]


def get_stock_info(symbol):
    stock_info = c.quote(symbol)
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

