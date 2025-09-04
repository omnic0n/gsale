from datetime import datetime, date, timedelta
from flask import Flask, session

from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session functionality

mysql = MySQL(app)

def set_dates(details):
    """Optimized date calculation for reports"""
    if details['year'] == "All":
        return "2000-01-01", "3000-01-01"
    
    year = int(details['year'])
    month = int(details['month'])
    date_obj = details['date']
    
    if details['type'] == "2":  # Year
        start_date = "{}-01-01".format(year)
        end_date = "{}-12-31".format(year)
    elif details['type'] == "1":  # Month
        start_date = "{}-{:02d}-01".format(year, month)
        # Calculate last day of month more efficiently
        if month == 12:
            end_date = "{}-12-31".format(year)
        else:
            next_month = month + 1
            next_year = year
            if next_month == 13:
                next_month = 1
                next_year = year + 1
            end_date = "{}-{:02d}-01".format(next_year, next_month)
            # Subtract one day to get last day of current month
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() - timedelta(days=1)
            end_date = end_date_obj.strftime('%Y-%m-%d')
    else:  # Date
        start_date = date_obj
        end_date = date_obj
    
    return start_date, end_date

def login_data(username, password, ip):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM accounts WHERE username = %s", (username, ))
        account = cursor.fetchone()

        if account and bcrypt.checkpw(password.encode('utf8'), account['password'].encode('UTF_8')):
            # Check if user is active
            if not account.get('is_active', True):
                f = open("/var/log/gsale/fail.log", "a")
                f.write(ip + " - " + username + " (deactivated account)" + "\n")
                f.close()
                return 'Account has been deactivated. Please contact an administrator.'
            
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account.get('name', account['username'])  # Use name if available, fallback to username
            session['email'] = account['email']  # Store email for footer display
            session['is_admin'] = account['is_admin']
            f = open("/var/log/gsale/success.log", "a")
            f.write(ip + " - " + username + "\n")
            f.close()
            return 'Logged in successfully!'
        else:
            f = open("/var/log/gsale/fail.log", "a")
            f.write(ip + " - " + username + ":" + password + "\n")
            f.close()
            return 'Incorrect username/password!'