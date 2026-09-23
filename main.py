from flask import Flask, render_template, redirect, flash, abort, session, request
from static.database.db import User, db
from static.blueprint.login import login_bp
from static.blueprint.user import user_bp
from dotenv import load_dotenv
from os import getenv,path
from openai import OpenAI

app = Flask(__name__)
app.register_blueprint(login_bp,url_prefix='/auth')
app.register_blueprint(user_bp,url_prefix='/dashboard')
app.secret_key = getenv('secret-key')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
BASE_DIR = path.dirname(path.abspath(__file__))
database_path = path.join(BASE_DIR, "static", "database", "db", "database.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"

db.init_app(app)

client = OpenAI(base_url='https://apihub.agnes-ai.com/v1', api_key=getenv('api_key'))

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

@app.route('/ai/send')
def send_msg():
    message = request.args.get('message','')
    data = request.args.get('data','')
    if(message.strip()==""):
        return 'لطفا پیام معتبر بفرستید.'
    response = client.chat.completions.create(
        model="agnes-2.5-flash",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"سلام تو باید همیشه فارسی جواب بدی و الان به پیامی که دارم میدم اهمیت نده. تو باید با توجه به داده ای که میدم فقط به سوال کاربر جواب بدی که برای مثال چرا کاربرام ریزش کرد یه احتمال بگو یا مثلا درصد و اینا. دقیقا یه امار میدم کاربر باتوجه به امار از تو سوال میکنه و تو باید راهنماییش کنی و فقط الان به سوال کاربر جواب بده و حواست باشه چیزی به غیر از امار و ریزش کاربر و داده و اینا پرسید جوابشو نده بهش بگو جوابتو نمیدم. آمار : \n{data}\n\n\nالان فقط به این سوال جواب بده : \n\n{message}"}
        ]
    )

    return response.choices[0].message.content

@app.route('/data-structure')
def data_structure_route():
    return render_template('blog/data-structure.html')

if __name__ == '__main__':
    app.run(debug=True)
