import os
import re
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final_project.db")

@app.after_request
def after_request(response):
    """ Ensure responses aren't cached """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Home/Search route
@app.route("/")
def index():
    """ Show homepage and allow users to search for shows/movies """

    # Render homepage
    return render_template("index.html")

# Watchlist Route
@app.route("/watchlist")
@login_required
def dashboard():
    """ Show dashboard """

    # Query DB for the users watchlist
    watchlist = [
        {
            "title": "The Office",
            "sites": "Peacock"
        },
        {
            "title": "Happy Endings",
            "sites": "Netflix"
        },
        {
            "title": "Modern Family",
            "sites": "Peacock, Hulu"
        },
        {
            "title": "The Amazing Spider-Man",
            "sites": "Prime Video"
        }
    ]

    # Get username
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])

    # Render watchlist and pass in user details and watchlist
    return render_template("watchlist.html", watchlist=watchlist, username=username[0]["username"])


# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in """

    # Forget any user_id
    session.clear()

    # User reached route via POST
    if request.method == "POST":

        # Ensure username and password was submitted
        if not request.form.get("username") or not request.form.get("password"):
            # SWAP FOR ALERT/FLASH
            flash("Username and/or password missing")
            return render_template("login.html")

        # Query DB for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect to dashboard/watchlist
        return redirect("/watchlist")

    # User reached route via GET
    else:
        return render_template("login.html")


# Logout Route
@app.route("/logout")
def logout():
    """ Log user out """

    # Forget any user_id
    session.clear()

    # Redirect user to homepage
    return redirect("/")


# Register Route
@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register new user """

    # User reached route via POST
    if request.method == "POST":

        # Ensure username, password, and confirmation was submitted and that passwords match
        # SWAP APOLOGIES FOR ALERTS/FLASHES
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            flash("Must fill out form completely")
            return render_template("register.html")
        if not request.form.get("password") == request.form.get("confirmation"):
            flash("Passwords do not match")
            return render_template("register.html")

        # Ensure proper password (8-20 chars, 1 lower, 1 upper, 1 digit, 1 special char)
        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$"
        pattern = re.compile(reg)
        match = re.search(pattern, request.form.get("password"))
        if not match:
            flash("Password does not meet criteria, please try again")
            return render_template("register.html")

        # Query DB to make sure username is unique
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username").strip())
        if len(rows) > 0:
            flash("Username is already in use, please try again")
            return render_template("register.html")

        # Store username and hashed password for table insert
        username = request.form.get("username").strip()
        hash = generate_password_hash(request.form.get("password").strip())

        # Add username and hashed password into DB and return id for session
        id = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        # Remember which user has registered/logged in
        session["user_id"] = id

        # Take user to dashboard/watchlist
        return redirect("/dashboard")

    # User reached route via GET
    else:
        return render_template("register.html")


# Search Route
@app.route("/search")
def search():

    # Ensure that the user entered a title and search type
    if not request.args.get("q"):
        flash("Please provide the title of a show or movie that you want to watch")
        return render_template("index.html")
    if not request.args.get("searchType"):
        flash("Please select 'Movie' or 'TV Series'")
        return render_template("index.html")

    # Use Flixed API to search for title
    title = request.args.get("q")
    type = request.args.get("searchType")
    print(type)
    results = lookup(title, type)

    # Checks if there is a current session to dynamically render "+ Watchlist" button
    if "user_id" in session:
        user = session["user_id"]
    else:
        user = None

    return render_template("results.html", results=results["results"], title=title, user=user)


# Wildcard Route
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    return apology("page not found", 404)