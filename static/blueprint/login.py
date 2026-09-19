from flask import Blueprint, render_template, abort, redirect, flash, request, session
from static.database.db import User, db

login_bp = Blueprint('auth', __name__,url_prefix='/auth')

@login_bp.route('/',methods=['GET','POST'])
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
        return render_template('page/auth.html',mode=mode,session=session)
    
    action_redirector = request.args.get('action_redirector','')
    complete = request.args.get('complete','')
    print(action_redirector,complete)
    username = request.form.get('usrname','')
    password = request.form.get('password','')
    if(username.strip()==''or password.strip()==''):
        flash('اسم یا رمز عبور نامعتبر.')
        return redirect(f'/auth?mode={action_redirector}')
    if(action_redirector=='login'):
        user = User.query.filter_by(username=username,password=password).first()
        if(user):
            session['excel_filepath'] = user.excel_filepath
            session['service_name'] = user.service_name
            session['userinfo'] = {'username':user.username,'email':user.email,'password':user.password}
            session['login'] = True
            flash('با موفقیت وارد شدید!')
            return redirect('/dashboard')
        else:
            flash('کاربر یافت نشد.')
            return redirect('/auth?mode=login')
    elif(action_redirector=='register'):
        email = request.form.get('email','')
        if not email.endswith('@gmail.com'):
            flash('ایمیل نامعبر.')
            return redirect('/auth?mode=register')
        if(User.query.filter_by(username=username,email=email,password=password).first()):
            flash('یکی از اطلاعات شما برای کاربر دیگری صدق میکند.')
            return redirect('/auth?mode=register')
        user = User(username=username,email=email,password=password)
        session['login'] = True
        session['excel_filepath'] = '-'
        session['service_name'] = '-'
        session['userinfo'] = {'username':user.username,'email':user.email,'password':user.password}
        db.session.add(user)
        db.session.commit()
        flash('با موفقیت وارد شدید')
        return redirect('/')
    return abort(404)

@login_bp.route('/logout')
def logout():
    session.clear()
    session['login'] = False
    return redirect('/auth?mode=login')