import os
import json

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")


@app.route("/")
@login_required
def index():
    """Homepage"""
    return render_template("index.html")


@app.route('/_get_post_json/', methods=['POST'])
def get_post_json():    
    
    # Receive data from user
    data = request.get_json()
    date = list(data.values())[0]
    qty = list(data.values())[1]
    ingr = list(data.values())[2]
    user = session["user_id"]
    
    # Delete the outdated items
    db.execute("DELETE FROM fridge WHERE (id,ingredients, qty, date) = (?,?,?,?)", user,ingr,qty ,date)
    
    return redirect("/myfridge")
    

@app.route("/myfridge", methods=["GET", "POST"])
@login_required
def myfridge():
    """User's list of food item list"""
    
    if request.method == "POST":

        if request.form['action'] == 'Remove':

            flash("Updated!")
            
        if request.form['action'] == 'Submit':
       
            ingr = request.form.get("ingredients")
            qty = request.form.get("qty")
            date = request.form.get("date")
            
            user = session["user_id"]

            if not request.form.get("ingredients"):
                return apology("Must provide ingredients")
            elif not request.form.get("qty"):
                return apology("Must provide quantity") 
            elif not request.form.get("date"):
                return apology("Must provide date")           

            db.execute("INSERT INTO fridge (id,ingredients, qty, date) VALUES (?,?,?,?)", user,ingr ,qty ,date)
            
            flash("Entry entered")
            
    #Update the food bank
    fridges = db.execute("SELECT * FROM fridge WHERE id = ? ORDER BY date", session["user_id"])
  
    return render_template("myfridge.html", fridges = fridges)

@app.route("/receipes", methods=["GET", "POST"])
@login_required
def receipes():
    """Add or show new receipes"""
    
    number = 5

    if request.method == "POST":
        
        ingr = request.form.getlist("ingredient")
        qty = request.form.getlist("quantity")
        c = request.form.getlist("cuisine")
        d = request.form.getlist("name")
                
        uni_id = db.execute("SELECT max(id) FROM receipe")
        x = uni_id[0]
        value = x['max(id)']

        if value == "NULL":
            value = 0
        else:
            new_value = int(value or 0) + 1    

                
        data_zip =zip(ingr,qty)
        data = list(data_zip)
                
                
        for i in data:
            db.execute("INSERT INTO receipe (id, ingredients, qty, cuisine, dish) VALUES (%s, %s, %s, %s, %s)",new_value,i[0],i[1],c,d)
                    
                        
        flash("Entry entered")

    receipes = db.execute("SELECT * FROM receipe")

    return render_template("receipes.html", number=number, receipes=receipes)

@app.route("/dishes", methods=["GET", "POST"])
@login_required
def dishes():
    """View dishes"""
    
    if request.method =="POST":

        search = request.form.getlist("search")
        results = db.execute("SELECT cuisine, dish FROM receipe WHERE dish = ? GROUP BY id", search)

    keyword = request.args.get('keyword')

    # List all of the dishes as defult
    if keyword != None:

        word = '%' + keyword + '%'
        dishes = db.execute("SELECT dish, cuisine FROM receipe WHERE dish LIKE ? GROUP BY id", word)

    #Find the matched dish    
    else:   
        dishes = db.execute("SELECT dish, cuisine, id FROM receipe GROUP BY id")

    return render_template("dishes.html", dishes = dishes)

@app.route("/measurements", methods=["GET", "POST"])
@login_required
def measurements():
    """Convert different measurements"""

    return render_template("measurements.html")

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

        # Remeber user's name
        session["user_name"] = rows[0]["username"]

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



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

            # Ensure username was submitted
            if not request.form.get("username"):
                return apology("must provide username", 400)

            # Ensure password was submitted
            elif not request.form.get("password"):
                return apology("must provide password", 400)

            # Check database for username existance
            rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

            print(rows)
            if len(rows) == 1:
                return apology("username already existed", 400)


            # Add the user name and password to the database
            username = request.form.get("username")
            password = request.form.get("password")
            password2 =request.form.get("confirmation")

            if password != password2:

                return apology("Passwords don't match", 400)

            hash_password = generate_password_hash(request.form.get("password"))

            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash_password)

            rows = db.execute("SELECT * FROM users WHERE username = ?", username)

            # Remember which user has logged in
            #session["user_id"] = rows[0]["id"]

            return redirect("/registered")

    else:

        return render_template("register.html")

@app.route("/registered", methods=["GET"])
def registered():

    return render_template("registered.html"),{"Refresh": "1; url=/login"}   

   
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    if request.method == "POST":
        if not request.form.get("old_password") or not request.form.get("new_password") or not request.form.get("confirm"):
            return apology("must provide password", 403)


        old = request.form.get("old_password")
        new = request.form.get("new_password")
        confirm = request.form.get("confirm")

        if new != confirm:
            return apology("2 passwords must match", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("old_password")):
            return apology("invalid password", 403)

        new = generate_password_hash(request.form.get("new_password"))

        db.execute("UPDATE users SET hash = ? WHERE id = ?", new, session["user_id"] )

        return redirect ("/")

    return render_template("profile.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
