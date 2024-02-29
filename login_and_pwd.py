from flask import Flask, render_template, request, redirect, url_for
from postgresDB_auth import authenticate_user

app =  Flask(__name__)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    result = authenticate_user(username, password)

    if result is not None:
        return f"Successful Login. Welcom Mr.{username} "
    else:
        return "Incorrect Username or Password"

if(__name__ == "__main__"):
    app.run(debug = True)