from flask import Flask, render_template, request, redirect, url_for, session
from flask import Blueprint
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

auth_api = Blueprint('auth_api', __name__)

@auth_api.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        addr = request.environ['HTTP_X_FORWARDED_FOR'].split(',')
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        msg = function.login_data(username=username, password=password, ip=addr[0])
        app.config['session'] = session
        if 'loggedin' in session:
            return redirect(url_for('index'))    
    return render_template('login.html', msg=msg)

@auth_api.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))