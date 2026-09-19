from flask import Flask, render_template, redirect, flash, abort, session, request
from static.database.db import User, db
from static.blueprint.login import login_bp
from static.blueprint.user import user_bp
from dotenv import load_dotenv
from os import getenv,path

app = Flask(__name__)
app.register_blueprint(login_bp,url_prefix='/auth')
app.register_blueprint(user_bp,url_prefix='/dashboard')
app.secret_key = getenv('secret-key')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
BASE_DIR = path.dirname(path.abspath(__file__))
database_path = path.join(BASE_DIR, "static", "database", "db", "database.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"

db.init_app(app)

with app.app_context():
    db.create_all()

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
    return render_template('page/plan.html',session=session)

@app.route('/data-structure')
def data_structure_route():
    return render_template('blog/data-structure.html')

if __name__ == '__main__':
    app.run(debug=True)