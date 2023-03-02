from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from flask import Flask,redirect, url_for, session


def set_dates(details):
    year = int(details['year'])
    month = int(details['month'])
    date = details['date']
    if(details['type'] == "Year"):
        print("year")
        start_date = ("%s-01-01") % (year)
        end_date = datetime.strptime(("%s-01-01") % (year + 1), '%Y-%m-%d').date() - timedelta(days=1)
    elif(details['type'] == "Month"):
        print("month")
        start_date = ("%s-%s-01") % (year, month)
        end_date = datetime.strptime(("%s-%s-01") % (year,month),'%Y-%m-%d').date() + relativedelta(months=1) - timedelta(days=1)
    else:
        start_date = date
        end_date = date
    return start_date, end_date

def login(session):
    if 'loggedin' in session:
        print(session['username'])
    else:
        print("not logged in")
        redirect(url_for('login'))