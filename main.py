from flask import Flask, render_template, redirect, flash, session, request
from dotenv import load_dotenv
from os import getenv

app = Flask(__name__)
app.secret_key = getenv('secret-key')

@app.route('/')
def index():
    if not session:
        session['login'] = False
    return render_template('index.html',session=session)

if __name__ == '__main__':
    app.run(debug=True)