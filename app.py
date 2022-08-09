import os
import psycopg2
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
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
db = SQL("sqlite:///stonks.db")

#Progres DataBase URL
if not os.environ.get('DATABASE_URL'):
    raise RuntimeError("DATABASE_URL NOT SET")
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

# Make sure API key is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")


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
    return render_template("dashboard.html")

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
        rows = cur.fetchone()
        # Ensure email exists and password is correct
        if rows is None:
            return render_template("login.html", error="Invalid Email or password")

        #Check password    
        if not check_password_hash(rows[3], (request.form.get("password"))):
            return render_template("login.html", error="Invalid Email or password")
        # Remember which user has logged in
        session["user_id"] = rows[0]

        # Redirect user to home page
        return redirect("/dashboard")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


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
        rows_uname = cur.fetchone()
        cur.execute("SELECT * FROM users WHERE email =%s;", (email,))
        rows_email = cur.fetchone()
        print(type(rows_uname), type(rows_email))
        cur.execute("SELECT * FROM users;")
        rows = cur.fetchall()
        print(rows)
        if(not username or not password or not email):
            return render_template("register.html",error="Empty Fields")

        if(rows_uname is not None):
            return render_template("register.html",error="Username Already Taken")

        if(rows_email is not None):
            return render_template("register.html",error="Email Already Used")

        if(not is_email(email)):
            return render_template("register.html",error="Invalid Email")

        hash = generate_password_hash(request.form.get("password"))
        cur.execute("INSERT INTO users (username,email,hash) VALUES (%s,%s,%s);", (username, email, hash))

        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        row = cur.fetchone()
        print(type(row), row, row[0])
        session["user_id"] = row[0]
        cur.execute("COMMIT")
        return redirect("/dashboard")

    return render_template("register.html")






@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")
