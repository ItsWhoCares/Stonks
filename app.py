import os
import psycopg2
import psycopg2.extras
import pyEX as p
import requests
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, Most_active, is_market_open, get_stock_info, news
from dbinterface import getBalance, oneYearMonthPrices, isBookmark, getBookmark
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
isnews = False

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Show portfolio of stocks"""
    return render_template("index.html")

@app.route("/dashboard")
@login_required
def dashboard():
    most_active_9 = Most_active()
    status = is_market_open()
    balance = getBalance(session["user_id"])
    return render_template("dashboard.html", status=status, most_active=most_active_9, balance=balance)


@app.route("/stocks/<stock_symbol>", methods=["GET","POST"])
@login_required
def stocks(stock_symbol):
    status = is_market_open()
    key_info = get_stock_info(stock_symbol)
    balance = getBalance(session["user_id"])
    if isnews:
        articles = fetch_news(stock_symbol)
    else:
        articles = None
    return render_template("stocks.html", status=status, key_info=key_info, articles=articles, balance=balance)

@app.route("/latest_price/<stock_symbol>", methods=["GET","POST"])
def latest_price(stock_symbol):
    price = get_stock_info(stock_symbol)
    return str(price["LatestPrice"])


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    row = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    balance = row[0]["cash"]

    if(request.method == "POST"):
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        stock = lookup(symbol)
        if(not stock):
            return apology("Invalid Symbol")

        bill = float(stock["price"] * float(shares))
        id = session["user_id"]



        if((balance - bill) < 0):
            return apology("Insufficient Balance")

        balance = balance - bill
        db.execute("UPDATE users SET cash = ? WHERE id = ?", balance, session["user_id"])
        db.execute("INSERT INTO transactions VALUES (?,?,?,?)", session["user_id"], symbol, shares, stock["price"])
        row = db.execute("SELECT * FROM portfolio WHERE id = ? AND symbol = ?", session["user_id"], symbol)
        if(len(row) == 0):
            db.execute("INSERT INTO portfolio VALUES (?,?,?)", session["user_id"], symbol, shares)
        db.execute("UPDATE portfolio SET shares = shares + ? WHERE id = ? AND symbol = ?", id, symbol, shares)

        return render_template("buy.html", done="Done", balance=balance)

    return render_template("buy.html", balance=balance)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
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
def portfolio():
    return render_template("portfolio.html")

@app.route("/watchlist")
@login_required
def watchlist():
    bookmarks = getBookmark(session["user_id"])
    status = is_market_open()
    balance = getBalance(session["user_id"])
    print(bookmarks)
    return render_template("watchlist.html", status=status, balance=balance, bookmarks=bookmarks)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
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
def sell():
    """Sell shares of stock"""
    return apology("TODO")


@app.route("/OneDayChart/<symbol>", methods=["GET"])
@login_required
def OneDayChart(symbol):
    api_key = 'SAOS0Y8B63XM4DPK'
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={api_key}"
    response = requests.get(url)

    stock_data = response.json()
    labels = []
    data = []
    chart = {
        "labels":[],
        "data":[]
    }
    for label in stock_data["Time Series (1min)"]:
        labels.append(label.split(" ")[1][:5])
    
    for label in stock_data["Time Series (1min)"]:
        data.append(round(float(stock_data["Time Series (1min)"][label]["4. close"]),2))

    for label in labels:
        chart["labels"].append(label)

    for dat in data:
        chart["data"].append(dat)
    chart["labels"].reverse()
    chart["data"].reverse()
    return chart


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
    results = db.execute("SELECT * FROM stocklist where symbol LIKE ? LIMIT 10;", symbol.upper() + "%")
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



@app.route("/bookmark/<symbol>/<todo>", methods=["GET"])
@login_required
def bookmark(symbol, todo):
    cur.execute("SELECT * FROM watchlist WHERE id=%s;",(session["user_id"],))
    res = getone()
    if res is not None and todo == "add":
        stock = db.execute("SELECT * FROM stocklist WHERE symbol=?", symbol)
        cur.execute("INSERT INTO watchlist VALUES(%s,%s,%s);",(session["user_id"], symbol.upper(), stock["name"]))
        cur.execute("COMMIT;")
        return True
    elif res is None and todo == "remove":
        cur.execute("DELETE watchlist WHERE id=%s AND symbol=%s;", (session["user_id"], symbol.upper()))
        cur.execute("COMMIT;")
        return True
    return False

