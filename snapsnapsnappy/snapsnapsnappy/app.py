"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, render_template, redirect, url_for, request, session
from hashlib import md5

import pymysql

app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

ROLE_USER = 1
ROLE_ADMIN = 2
ROLE_TEACHER = 3

# The only connection to your MySQL database - the library of accounts.
wsgi_app = app.wsgi_app
def create_connection():
    return pymysql.connect(  
        host = '127.0.0.1',
        user = 'root',
        password = 'Akamanah001',
        db = 'waypoon',
        charset = 'utf8mb4',
        cursorclass = pymysql.cursors.DictCursor
        )

# Entrance security for the school database; who knows if some uninvited guest might wipe the database clean?
@app.route('/')
def index():
    if session.get("loggedIn"):
        if session["loggedIn"]:
            return render_template("/menu.html")
    return redirect("/userLogin")

# Everyone needs to start somewhere. /create is that somewhere.
@app.route('/create', methods =["GET","POST"])
def create():
    if request.method == "POST":
        userName = request.form["userName"]
        cameraID = request.form["userID"]
        roleID = request.form["roleID"]
        password = request.form["password"]
        password = md5(password.encode()).hexdigest()

        connection = create_connection()

        with connection.cursor() as cursor:
                sql = "INSERT INTO camerausers(userName, roleID, password) VALUES (%s, %s, %s);"
                vals = (userName, roleID, password)
                try:
                    cursor.execute(sql, vals)
                    connection.commit()
                except Exception as e:
                    print(str(e), flush = True)
                finally:
                    connection.close()
        return redirect("/")
    else:
        return render_template("create.html")

# Want to buy a camera? Sign up here, here and there. Remember your order, or you'll lose your money.
@app.route('/cameraOrder', methods =["GET","POST"])
def cameraOrder():
    if request.method == "POST":
        cameraName = request.form["cameraName"]
        cameraID = request.form["cameraID"]
        cameraUse = request.form["cameraUse"]

        connection = create_connection()

        with connection.cursor() as cursor:
            # Don't leave a box blank. It's rude and we need the info for purchases.
                sql = "INSERT INTO buylist(cameraID, cameraName, cameraUse) VALUES (%s, %s, %s);"
                vals = (cameraID, cameraName, cameraUse)
                try:
                    cursor.execute(sql, vals)
                    connection.commit()
                except Exception as e:
                    print(str(e), flush = True)
                finally:
                    connection.close()
        return redirect("/")
    else:
        return render_template("cameraOrder.html")

# The school is not a public bar. No account means no entry.
@app.route("/userLogin", methods=["GET", "POST"])
def login():
    error = None
    if request.method == 'POST':
        userName = request.form["userName"]
        password = request.form["password"]
        password = md5(password.encode()).hexdigest()
        connection = create_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM camerausers WHERE userName = %s AND password = %s"
            vals = (userName, password)
            cursor.execute(sql, vals)
            users = cursor.fetchall()
        connection.close()
        if len(users) == 0:
            #Login failed. You're not one of us!
            return render_template("nothere.html")
        else:
            #Login succeeded. Welcome, friend!
            user = users[0]
            session['userName'] = user['userName']
            session['userID'] = user['userID']
            session["roleID"] = user['roleID']
            session['password'] = user['password']
            session["loggedIn"] = True
            return redirect("menu")
    else:
        return render_template("userLogin.html", error=error)

# Everything available is here.
@app.route("/menu")
def menu():
    connection = create_connection()
    with connection.cursor() as cursor:
        sql  = "SELECT userID, cameraID, cameraUse, cameraName FROM buylist;"
        cursor.execute(sql)
        buylist = cursor.fetchall()
        connection.close()
        print (menu)
    return render_template("menu.html", buylist = buylist)

# A list of cameras the admins added. To allocate it to another account, click here.
@app.route('/cameraPage')
def cameraPage():
    if session["roleID"] == ROLE_ADMIN:
        connection = create_connection()
        with connection.cursor() as cursor:
            sql  = "SELECT userID, cameraID, cameraUse, cameraName FROM buylist;"
            cursor.execute(sql)
            buylist = cursor.fetchall()
            connection.close()
            print (menu)
            return render_template("cameraPage.html", buylist = buylist)
    else:
        return redirect("/")

# Admin's the guy who determines what gets what resources. Resistance is futile.
@app.route('/loan')
def loan():
    if session["roleID"] == ROLE_ADMIN:
        connection = create_connection()
        with connection.cursor() as cursor:
            sql  = "SELECT userName, userID, roleID FROM camerausers;"
            cursor.execute(sql)
            camerausers = cursor.fetchall()
            connection.close()
            return render_template("loan.html", camerausers = camerausers)
    else:
        return redirect("/")

# Because nobody loves staying at school 24/7,; there's always an exit.
@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

# Mistakes are made to be corrected/changed. /update is here for you!
@app.route('/update', methods = ["GET", "POST"])
def update():
    if session["roleID"] == ROLE_ADMIN:
        if request.method == "POST":
            cameraName = request.form["cameraName"]
            cameraID = request.form["cameraID"]
            cameraUse = request.form["cameraUse"]
 
            connection = create_connection()

            with connection.cursor() as cursor:
                # Everything you typed in those boxes get sent to the database.
                sql = "UPDATE buylist SET cameraName = %s, cameraID = %s, cameraUse=%;"
                vals = (cameraName, cameraID, cameraUse)
                cursor.execute(sql, vals)
                connection.commit()
                connection.close()
            return redirect("/menu")
        else:
            userID = request.args["userID"]
            connection = create_connection()
            with connection.cursor() as cursor:
                sql = "SELECT * FROM buylist WHERE userID = %s;"
                cursor.execute(sql, userID)
                cursor.fetchall()
                connection.close()
            return render_template("update.html")
    else:
        return redirect("/")

# You don't want a camera anymore so you remove it with /delete!
@app.route('/delete', methods = ["GET", "POST"])
def delete():
    #So when person A clicks the DELETE button next to their order, they don't delete person B's.
    cameraID = int(request.args["userID"])
    connection = create_connection()
    with connection.cursor() as cursor:
        sql = "DELETE FROM buylist WHERE userID = %s;"
        vals = (userID)
        cursor.execute(sql, vals)
        connection.commit()
        connection.close()
    return redirect('/')

# A place for the internet to travel to your program.
if __name__ == '__main__':
    import os
    app.secret_key = os.urandom(12)
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
