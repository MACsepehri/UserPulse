from flask import Flask, render_template, redirect, flash, abort, session, request
from static.blueprint.login import login_bp
from dotenv import load_dotenv
from os import getenv

app = Flask(__name__)
app.register_blueprint(login_bp,url_prefix='/auth')
app.secret_key = getenv('secret-key')

@app.route('/')
def index():
    if not session:
        session['login'] = False
    return render_template('index.html',session=session)

@app.route('/plan')
def plan():
    if not session:
        session['login'] = False
    plan_type = request.args.get('pt','')
    if(plan_type=='')or(plan_type!='free'):
        return abort(404)
    if not session['login']:
        return redirect('/auth?mode=login')
    return render_template('page/plan.html')

if __name__ == '__main__':
    app.run(debug=True)