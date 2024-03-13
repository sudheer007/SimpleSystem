from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from postgresDB_auth import CredentialsDB

db = CredentialsDB()
authenticate_user = db.authenticate_user
get_todo = db.get_todo

app =  Flask(__name__)

app.secret_key = 'secret_key_0177#@!%$&'

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    result = authenticate_user(username, password)
    # print("api:",result)

    if result:
        #return f"Successful Login. Welcom Mr.{username} "
        session['username'] = username
        return redirect(url_for('dashboard'))

    else:
        return "Incorrect Username or Password"

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    else:
        return render_template('dashboard.html')
    
@app.route('/todos')
def fetch_todo():
    if 'username' not in session:
        return jsonify({'error': 'user not logged in'}), 401
    username = session['username']
    result = get_todo(username)

    return jsonify(result)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if(__name__ == "__main__"):
    app.run(debug = True)