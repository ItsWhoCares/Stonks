import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

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
db = SQL("sqlite:///users.db")

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
# @login_required
def index():
    """Show portfolio of stocks"""
    return "Hello World"


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

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

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

    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    if(request.method == "POST"):
        rows = db.execute("SELECT * FROM users WHERE username =?;", username)
        if(len(rows) == 1):
            return apology("Username Already Taken")

        if(password != confirmation):
            return apology("Passwords Don't Match")

        if(not username or not password or not confirmation):
            return apology("Empty Fields")

        hash = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (username,hash) VALUES (?,?);", username , hash)

        row = db.execute("SELECT * FROM users WHERE username=?", username)
        session["user_id"] = row[0]["id"]
        return redirect("/register")

    return render_template("register.html")






@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")
