import os
import psycopg2
import psycopg2.extras
import pyEX as p
import requests
import json
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

# from helpers import apology, login_required, lookup, usd, Most_active, is_market_open, get_stock_info, news, getTopGainers
from helpers import *
from dbinterface import *
from pyisemail import is_email
# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///stocklist.db")

#Progres DataBase URL
if not os.environ.get('DATABASE_URL'):
    raise RuntimeError("DATABASE_URL NOT SET")
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# Make sure API key is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")


#Link IEX 
if not os.environ.get('IEX_API_KEY'):
    raise RuntimeError('IEX_API_KEY NOT SET')
IEX_API_KEY = os.environ['IEX_API_KEY']
c = p.Client(api_token=IEX_API_KEY) 
api_key_two = IEX_API_KEY

#is news on
# isnews = False

def db_con(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not os.environ.get('DATABASE_URL'):
            raise RuntimeError("DATABASE_URL NOT SET")
        try:
            cur.execute("SELECT * FROM users")
            cur.fetchone()
        except:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return f(*args, **kwargs)
    return decorated_function


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    if not os.environ.get('DATABASE_URL'):
        raise RuntimeError("DATABASE_URL NOT SET")
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    """Show portfolio of stocks"""
    return render_template("index.html")

@app.route("/dashboard")
@login_required
@db_con
def dashboard():
    printTables()
    most_active_9 = Most_active()
    status = is_market_open()
    balance = getBalancef(session["user_id"])
    if session["user_id"] == 12:
        return render_template("specialdash.html", status=status, most_active=most_active_9, balance=balance)

    return render_template("dashboard.html", status=status, most_active=most_active_9, balance=balance)


@app.route("/trends/<ReqDataType>")
@login_required
@db_con
def trends(ReqDataType):
    status = is_market_open()
    balance = getBalancef(session["user_id"])
    stocks = getTopGainers()
    match ReqDataType:
        case "topGainers":
            stocks = getTopGainers()
        case "topLosers":
            stocks = getTopLosers()
        case "topVolume":
            stocks = getTopVolume()
    return render_template("trends.html", status=status, balance=balance, stocks=stocks)


@app.route("/stocks/<stock_symbol>", methods=["GET","POST"])
@login_required
@db_con
def stocks(stock_symbol):
    status = is_market_open()
    key_info = get_stock_info(stock_symbol)
    balance = getBalancef(session["user_id"])
    articles = news(stock_symbol)
    isbookmarked = isBookmark(session["user_id"], stock_symbol)
    return render_template("stocks.html", status=status, key_info=key_info, articles=articles, balance=balance, isbookmarked=isbookmarked)

@app.route("/latest_price/<stock_symbol>", methods=["GET","POST"])
def latest_price(stock_symbol):
    price = get_stock_info(stock_symbol)
    return str(price["LatestPrice"])


@app.route("/login", methods=["GET", "POST"])
@db_con
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username and password was submitted
        if not request.form.get("email") or not request.form.get("password"):
            return render_template("login.html", error="Invalid Email or password")


        # Query database for email
        cur.execute("SELECT * FROM users WHERE email = %s", (request.form.get("email"),))
        row = getone()
        # Ensure email exists and password is correct
        if row is None:
            return render_template("login.html", error="Invalid Email or password")

        #Check password    
        if not check_password_hash(row["hash"], (request.form.get("password"))):
            return render_template("login.html", error="Invalid Email or password")
        # Remember which user has logged in
        session["user_id"] = row["id"]

        # Redirect user to home page
        return redirect("/dashboard")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/portfolio")
@login_required
@db_con
def portfolio():
    status = is_market_open()
    balance = getBalancef(session["user_id"])
    stocks = getPortfolio(session["user_id"])
    return render_template("portfolio.html", status=status, balance=balance, stocks=stocks)

@app.route("/watchlist")
@login_required
@db_con
def watchlist():
    bookmarks = getBookmark(session["user_id"])
    status = is_market_open()
    balance = getBalancef(session["user_id"])
    return render_template("watchlist.html", status=status, balance=balance, bookmarks=bookmarks)

@app.route("/logout")
@db_con
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
@db_con
def quote():
    """Get stock quote."""

    if(request.method == "POST"):
        symbol = request.form.get("symbol")
        if(not symbol):
            return render_template("quote.html")

        quote = lookup(symbol)
        if(not quote):
            return render_template("quote.html")

        # quote["price"] = usd(quote["price"])
        return render_template("quoted.html", quote=quote)



    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
@db_con
def register():
    """Register user"""
    if(request.method == "POST"):
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        cur.execute("SELECT * FROM users WHERE username =%s;", (username,))
        row_uname = getone()
        cur.execute("SELECT * FROM users WHERE email =%s;", (email,))
        row_email = getone()
        if(not username or not password or not email):
            return render_template("register.html",error="Empty Fields")

        if(row_uname is not None):
            return render_template("register.html",error="Username Already Taken")

        if(row_email is not None):
            return render_template("register.html",error="Email Already Used")

        if(not is_email(email)):
            return render_template("register.html",error="Invalid Email")

        hash = generate_password_hash(request.form.get("password"))
        cur.execute("INSERT INTO users (username,email,hash) VALUES (%s,%s,%s);", (username, email, hash))

        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        row = getone()
        session["user_id"] = row["id"]
        cur.execute("COMMIT")
        return redirect("/dashboard")

    return render_template("register.html")






@app.route("/sell", methods=["GET", "POST"])
@login_required
@db_con
def sell():
    """Sell shares of stock"""
    return apology("TODO")


@app.route("/OneDayChart/<symbol>", methods=["GET"])
@login_required
def OneDayChart(symbol):
    return getOneDayChart(symbol)


@app.route("/OneMonthChart/<symbol>", methods=["GET"])
@login_required
def OneMonthChart(symbol):
    stock_data = oneYearMonthPrices(symbol)["oneMonth"]
    chart = {
        "labels":[],
        "data":[]
    }
    for day in stock_data["chart"]:
        chart["labels"].append(day["label"])
        chart["data"].append(day["close"])

    return chart


@app.route("/OneYearChart/<symbol>", methods=["GET"])
@login_required
def OneYearChart(symbol):
    stock_data = oneYearMonthPrices(symbol)["oneYear"]
    chart = {
        "labels":[],
        "data":[]
    }
    for day in stock_data["chart"]:
        chart["labels"].append(day["label"])
        chart["data"].append(day["close"])

    return chart


# def fetch_news(symbol):
#     row = cur.execute("SELECT * FROM news WHERE Symbol=%s;", (symbol,))
    

#Search for stock using symbol
@app.route("/search/<symbol>", methods=["GET"])
def search(symbol):
    results = db.execute("SELECT * FROM stocklist where symbol LIKE ? OR name LIKE ? LIMIT 10;", symbol.upper() + "%", symbol.upper() + "%")
    return results

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



@app.route("/bookmark/<symbol>", methods=["GET"])
@login_required
@db_con
def bookmark(symbol):
    cur.execute("SELECT * FROM watchlist WHERE id=%s AND symbol=%s;",(session["user_id"],symbol.upper()))
    res = getone()
    if res is None:
        stock = db.execute("SELECT * FROM stocklist WHERE symbol=?", symbol)
        cur.execute("INSERT INTO watchlist VALUES(%s,%s);",(session["user_id"], symbol.upper()))
        cur.execute("COMMIT;")
        return json.dumps("added")
    elif res is not None:
        cur.execute("DELETE FROM watchlist WHERE id=%s AND symbol=%s;", (session["user_id"], symbol.upper()))
        cur.execute("COMMIT;")
        return json.dumps("removed")
    return json.dumps("error")

@app.route("/getData/<ReqDataType>")
@login_required
def getData(ReqDataType):
    match ReqDataType:
        case "topGainers":
            return getTopGainers()
        case "topLosers":
            return getTopLosers()
        case "topVolume":
            return getTopVolume()
        case "balance":
            return {"balance": getBalancef(session["user_id"])}
    return "Error"

# @app.route("/getData/balance")
# @login_required
# def getbalance():
#     return {
#         "balance": getBalancef(session["user_id"])
#     }

@app.route("/buyStock/<symbol>/<quantity>")
@login_required
@db_con
def buyStock(symbol, quantity):
    # if(not is_market_open()):
    #     return{
    #         "status": "Failure",
    #         "errorMsg": "Market is closed"
    #     }
    stockPrice = get_stock_price(symbol, 4)
    bill = round(stockPrice * float(quantity))
    if canBuy(bill, session["user_id"]):
        makeBuyTransaction(session["user_id"], symbol.upper(), stockPrice, quantity)
        cur.execute("COMMIT;")
        return {
        "status": "Success"
        }
    return {
        "status": "Failure",
        "errorMsg": "Insufficient Balance"
    }
@app.route("/sellStock/<symbol>/<tid>")
@login_required
@db_con
def sellStock(symbol, tid):
    # if(not is_market_open()):
    #     return{
    #         "status": "Failure",
    #         "errorMsg": "Market is closed"
    #     }
    stockPrice = get_stock_price(symbol, 4)
    if canSell(session["user_id"], symbol.upper(), tid):
        makeSellTransaction(session["user_id"], tid, stockPrice)
        return {
        "status": "Success"
        }
    return {
        "status": "Failure"
    }
    
    
    
@app.route("/addCredits")
@login_required
def addCredits():
    if not credit(session["user_id"], 10000):
        return {
            "msg": "Arre bas kar pagli" 
        }
    return {
        "msg": "Error"
    }
    
@app.route("/getmybalance")
@login_required
def getmybalance():
    return {
        "balance": getBalancef(session["user_id"])
    }
    
@app.route("/getmytransactions")
@login_required
def getmytransactions():
    cur.execute("SELECT * FROM transactions WHERE id=%s;", (session["user_id"],))
    return getall()
