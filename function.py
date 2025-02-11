from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from flask import Flask, session
from flask_session import Session

from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

mysql = MySQL(app)

def set_dates(details):
    if(details['year'] == "All"):
         start_date = "2000-01-01"
         end_date = "3000-01-01"
    else:
        year = int(details['year'])
        month = int(details['month'])
        date = details['date']
        if(details['type'] == "2"):
            start_date = ("%s-01-01") % (year)
            end_date = datetime.strptime(("%s-01-01") % (year + 1), '%Y-%m-%d').date() - timedelta(days=1)
        elif(details['type'] == "1"):
            start_date = ("%s-%s-01") % (year, month)
            end_date = datetime.strptime(("%s-%s-01") % (year,month),'%Y-%m-%d').date() + relativedelta(months=1) - timedelta(days=1)
        else:
            start_date = date
            end_date = date
    return start_date, end_date

def login_data(username, password, ip):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM accounts WHERE username = %s", (username, ))
        account = cursor.fetchone()

        if account and bcrypt.checkpw(password.encode('utf8'), account['password'].encode('UTF_8')):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            f = open("/var/log/gsale/success.log", "a")
            f.write(ip + " - " + username + "\n")
            f.close()
            return 'Logged in successfully!'
        else:
            f = open("/var/log/gsale/fail.log", "a")
            f.write(ip + " - " + username + ":" + password + "\n")
            f.close()
            return 'Incorrect username/password!'