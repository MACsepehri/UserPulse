from flask import Blueprint, render_template, abort, redirect, flash, request, session
from werkzeug.security import check_password_hash
from static.database.db import User, db
import os

user_bp = Blueprint('dashboard', __name__,url_prefix='/dashboard')

@user_bp.route('/')
def dashboard():
    if not session:
        session['login'] = False
    if not session['login']:
        flash('لطفا ابتدا وارد حساب خود شوید.')
        return redirect('/auth?mode=login')
    return render_template('dashboard/dashboard.html',session=session)

@user_bp.route('/create-service',methods=['POST'])
def create_user():
    if not session:
        session['login'] = False
    if not session['login']:
        flash('لطفا ابتدا وارد حساب خود شوید.')
        return redirect('/auth?mode=login')
    
    service_name = request.form.get('service-name','')
    service_desc = request.form.get('service-desc','')
    if(service_name==''or service_desc==''):
        flash('لطفا تمامی مقادیر را وارد کنید.')
        return redirect('/dashboard#section-one')
    user = User(username=session['userinfo']['username'],email=session['userinfo']['email'],password=session['userinfo']['password'])
    user.service_name = service_name
    user.service_desc = service_desc
    db.session.commit()
    session['service_name'] = service_name
    session['service_desc'] = service_desc
    flash('سرویس با موفقیت ساخته شد.')
    return redirect('/dashboard/')

@user_bp.route('/delete-service')
def delete_service():
    if not session:
        session['login'] = False
    if not session['login']:
        flash('لطفا ابتدا وارد حساب خود شوید.')
        return redirect('/auth?mode=login')
    password = request.args.get('password','')
    if (session['userinfo']['password']==password):
        user = User(username=session['userinfo']['username'],email=session['userinfo']['email'],password=session['userinfo']['password'])
        if(user):
            if(user.service_name==''or user.service_desc==''):
                flash('شما سرویسی ندارید که بخواهید حذف کنید.')
                return redirect('/dashboard/')
            user.service_name = '-'
            user.service_desc = '-'
            session['service_name'] = '-'
            session['service_desc'] = '-'
            db.session.commit()
            flash('سرویس با موفقیت حذف شد')
            return redirect('/dashboard/')
        flash('کاربر پیدا نشد.')
        return redirect('/auth?mode=login')
    flash('رمز عبور اشتباه است.')
    return redirect('/dashboard/')

@user_bp.route('/service',methods=['GET','POST'])
def view_service():
    if not session:
        session['login'] = False
    if not session['login']:
        flash('لطفا ابتدا وارد حساب خود شوید.')
        return redirect('/auth?mode=login')
    password = request.args.get('password','')
    send_file = request.args.get('send_file','')
    method = request.method.lower()
    if(method=='get'):
        if(password!=session['userinfo']['password']):
            flash('کاربر پیدا نشد.')
            return redirect('/dashboard#section-one')
        user = User(username=session['userinfo']['username'],email=session['userinfo']['email'],password=session['userinfo']['password'])
        if not user:
            flash('ابتدا وارد شوید.')
            return redirect('/auth?mode=login')
        if(user.service_name=='-'or user.service_desc=='-'):
            flash('شما سرویس ندارید')
            return redirect('/dashboard#section-one')
        return render_template('dashboard/service.html',session=session,user=user)
    else:
        if(send_file!='True'):
            return abort(404)
        csv_file = request.files.get('file')
        if csv_file is None or csv_file.filename == '':
            flash('فایل نامعتبر. فایلی آپلود نشده است.')
            return redirect(f'/dashboard/service?password={session["userinfo"]["password"]}')

        extension = os.path.splitext(csv_file.filename)[1].lower()

        if extension != '.csv':
            flash('فایل نامعتبر. فایل باید با پسوند .csv باشد.')
            return redirect(f'/dashboard/service?password={session["userinfo"]["password"]}')
        user = User(username=session['userinfo']['username'],email=session['userinfo']['email'],password=session['userinfo']['password'])
        if not user:
            flash('کاربر پیدا نشد.')
            return redirect('/auth?mode=login')
        if not os.path.exists(f'static/src/{session["userinfo"]["username"]}'):
            os.mkdir(f'static/src/{session["userinfo"]["username"]}')
        user.excel_filepath = f'static/src/{session["userinfo"]["username"]}/{csv_file.filename}'
        csv_file.save(user.excel_filepath)
        db.session.commit()
        flash('فایل با موفقیت ذحیره شد.')
        return redirect(f'/dashboard/service?password={session["userinfo"]["password"]}')