from flask import Blueprint, render_template, abort, redirect, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from static.database.db import User, db

login_bp = Blueprint('auth', __name__, url_prefix='/auth')


@login_bp.route('/', methods=['GET', 'POST'])
def login():

    if 'login' not in session:
        session['login'] = False

    if session['login']:
        return redirect('/dashboard')

    if request.method == 'GET':
        mode = request.args.get('mode', '')

        if mode not in ('login', 'register'):
            abort(404)

        return render_template(
            'page/auth.html',
            mode=mode,
            session=session
        )

    action_redirector = request.args.get('action_redirector', '')

    username = request.form.get('usrname', '').strip()
    password = request.form.get('password', '')
    hashed_password = generate_password_hash(password)

    if not username or not password:
        flash('اسم یا رمز عبور نامعتبر.')
        return redirect(f'/auth?mode={action_redirector}')

    if action_redirector == 'login':

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            session['login'] = True
            session['excel_filepath'] = user.excel_filepath
            session['service_name'] = user.service_name

            session['userinfo'] = {
                'username': user.username,
                'email': user.email,
                'password': hashed_password
            }

            flash('با موفقیت وارد شدید!')
            return redirect('/dashboard')

        flash('نام کاربری یا رمز عبور اشتباه است.')
        return redirect('/auth?mode=login')

    elif action_redirector == 'register':

        email = request.form.get('email', '').strip()

        if not email.endswith('@gmail.com'):
            flash('ایمیل نامعتبر.')
            return redirect('/auth?mode=register')

        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email)
        ).first()

        if existing_user:
            flash('نام کاربری یا ایمیل قبلاً استفاده شده است.')
            return redirect('/auth?mode=register')

        user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        session['login'] = True
        session['password'] = hashed_password
        session['excel_filepath'] = user.excel_filepath
        session['service_name'] = user.service_name

        session['userinfo'] = {
            'username': user.username,
            'email': user.email,
            'password': hashed_password
        }

        flash('با موفقیت ثبت‌نام و وارد شدید.')
        return redirect('/')

    abort(404)


@login_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/auth?mode=login')