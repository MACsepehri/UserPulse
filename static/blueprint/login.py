from flask import Blueprint, render_template, abort, redirect, request, session
from static.database.db import User, db

login_bp = Blueprint('auth', __name__,url_prefix='/auth')

@login_bp.route('/')
def login():
    method = request.method.lower()

    if not session:
        session['login'] = True
    if session['login']:
        return redirect('/dashboard')
    if(method=='get'):
        mode = request.args.get('mode', '')
        if mode not in ('login', 'register'):
            abort(404)
        return render_template('page/auth.html',mode=mode)
    
    action_redirector = request.args.get('action_redirector','')
    complete = request.args.get('complete','')
    if(complete!='True'or action_redirector!='register' or action_redirector!='login'):
        return abort(404)
    username = request.form.get('usrname','')
    password = request.form.get('password','')
    if(username.strip()==''or password.strip()==''):
        flash('اسم یا رمز عبور نامعتبر.')
        return redirect(f'/auth?mode={action_redirector}')
    if(action_redirector=='login'):
        user = User.query.filter_by(username=username,password=password).first()
        if(user):
            flash('با موفقیت وارد شدید!')
            return redirect('/dashboard')
        else:
            flash('کاربر یافت نشد.')
            return redirect('/auth?mode=login')
    else:
        email = request.form.get('email','')
        if not email.endswith('@gmail.com'):
            flash('ایمیل نامعبر.')
            return redirect('/auth?mode=register')
        user = User(username=username,email=email,password=password)
        db.session.add(user)
        db.session.commit()
        flash('با موفقیت وارد شدید')
        #set session and save user projects in db