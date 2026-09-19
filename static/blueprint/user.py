from flask import Blueprint, render_template, abort, redirect, flash, request, session
from static.database.db import User, db
from service import BaseModel
import pandas as pd
import shutil
import os
import ast

user_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@user_bp.route('/')
def dashboard():
    if not session:
        session['login'] = False

    if not session['login']:
        flash('لطفا ابتدا وارد حساب خود شوید.')
        return redirect('/auth?mode=login')

    return render_template(
        'dashboard/dashboard.html',
        session=session
    )


@user_bp.route('/create-service', methods=['POST'])
def create_service():
    if not session:
        session['login'] = False

    if not session['login']:
        flash('لطفا ابتدا وارد حساب خود شوید.')
        return redirect('/auth?mode=login')

    service_name = request.form.get('service-name', '')
    service_desc = request.form.get('service-desc', '')

    if service_name == '' or service_desc == '':
        flash('لطفا تمامی مقادیر را وارد کنید.')
        return redirect('/dashboard#section-one')

    user = User.query.filter_by(
        username=session['userinfo']['username'],
        email=session['userinfo']['email'],
        password=session['userinfo']['password']
    ).first()

    if not user:
        flash('کاربر پیدا نشد.')
        return redirect('/auth?mode=login')

    user.service_name = service_name
    user.service_desc = service_desc

    session['service_name'] = service_name
    session['service_desc'] = service_desc

    db.session.commit()

    flash('سرویس با موفقیت ساخته شد.')
    return redirect('/dashboard/')


@user_bp.route('/delete-service')
def delete_service():
    if not session:
        session['login'] = False

    if not session['login']:
        flash('لطفا ابتدا وارد حساب خود شوید.')
        return redirect('/auth?mode=login')

    password = request.args.get('password', '')

    if session['userinfo']['password'] == password:
        user = User.query.filter_by(
            username=session['userinfo']['username'],
            email=session['userinfo']['email'],
            password=session['userinfo']['password']
        ).first()

        if user:
            if user.service_name == '' or user.service_desc == '':
                flash('شما سرویسی ندارید که بخواهید حذف کنید.')
                return redirect('/dashboard/')

            user.service_name = '-'
            user.service_desc = '-'

            session['service_name'] = '-'
            session['service_desc'] = '-'

            for listdir in os.listdir('static/src'):
                if listdir == session['userinfo']['username']:
                    shutil.rmtree(f'static/src/{listdir}')

            db.session.commit()

            flash('سرویس با موفقیت حذف شد')
            return redirect('/dashboard/')

        flash('کاربر پیدا نشد.')
        return redirect('/auth?mode=login')

    flash('رمز عبور اشتباه است.')
    return redirect('/dashboard/')


@user_bp.route('/service', methods=['GET', 'POST'])
def view_service():
    if not session:
        session['login'] = False

    if not session['login']:
        flash('لطفا ابتدا وارد حساب خود شوید.')
        return redirect('/auth?mode=login')

    password = request.args.get('password', '')
    send_file = request.args.get('send_file', '')
    method = request.method.lower()

    if method == 'get':
        if password != session['userinfo']['password']:
            flash('کاربر پیدا نشد.')
            return redirect('/dashboard#section-one')

        user = User.query.filter_by(password=password).first()

        if not user:
            flash('ابتدا وارد شوید.')
            return redirect('/auth?mode=login')

        if not user.service_name or not user.service_desc:
            flash('شما سرویسی ندارید.')
            return redirect('/dashboard#section-one')

        return render_template(
            'dashboard/service.html',
            session=session,
            user=user
        )

    if send_file != 'True':
        return abort(404)

    csv_file = request.files.get('file')

    if csv_file is None or csv_file.filename == '':
        flash('فایل نامعتبر. فایلی آپلود نشده است.')
        return redirect(
            f'/dashboard/service?password={session["userinfo"]["password"]}'
        )

    extension = os.path.splitext(csv_file.filename)[1].lower()

    if extension != '.csv':
        flash('فایل نامعتبر. فایل باید با پسوند .csv باشد.')
        return redirect(
            f'/dashboard/service?password={session["userinfo"]["password"]}'
        )

    user = User.query.filter_by(
        username=session['userinfo']['username'],
        email=session['userinfo']['email'],
        password=session['userinfo']['password']
    ).first()

    if not user:
        flash('کاربر پیدا نشد.')
        return redirect('/auth?mode=login')

    user_directory = f'static/src/{session["userinfo"]["username"]}'

    if not os.path.exists(user_directory):
        os.mkdir(user_directory)

    filepath = f'{user_directory}/{csv_file.filename}'

    session['excel_filepath'] = filepath
    user.excel_filepath = filepath

    csv_file.save(filepath)

    db.session.commit()

    flash('فایل با موفقیت ذخیره شد.')

    return redirect(
        f'/dashboard/service?password={session["userinfo"]["password"]}'
    )


@user_bp.route('/check-file')
def check_file():
    if not session:
        session['login'] = False

    if not session['login']:
        flash('لطفا ابتدا وارد حساب خود شوید.')
        return redirect('/auth?mode=login')

    password = request.args.get('password', '')

    if password != session['userinfo']['password']:
        flash('کاربر پیدا نشد.')
        return redirect('/auth?mode=login')

    user = User.query.filter_by(
        username=session['userinfo']['username'],
        email=session['userinfo']['email'],
        password=session['userinfo']['password']
    ).first()

    if not user:
        flash('کاربر پیدا نشد.')
        return redirect('/auth?mode=login')

    if not user.excel_filepath or not os.path.exists(user.excel_filepath):
        flash('ابتدا فایل CSV خود را آپلود کنید.')
        return redirect(
            f'/dashboard/service?password={session["userinfo"]["password"]}'
        )

    model = BaseModel()

    try:
        df = pd.read_csv(user.excel_filepath)

        required_columns = [
            'تعداد بازدید کاربر از وبسایت',
            'خدمات وبسایت',
            'پر بازدید ترین سرویس ها',
            'تاریخ استفاده ی پر بازدید ترین سرویس ها',
            'کم بازدید ترین سرویس ها',
            'تاریخ استفاده ی کم بازدید ترین سرویس ها',
            'تاریخ بازدید سایت',
            'اطلاعات کاربر',
            'نام ستون های اطلاعات کاربری'
        ]

        for column in required_columns:
            if column not in df.columns:
                raise ValueError('Invalid CSV structure')

        for _, row in df.iterrows():
            data = [
                int(row['تعداد بازدید کاربر از وبسایت']),
                ast.literal_eval(row['خدمات وبسایت']),
                ast.literal_eval(row['پر بازدید ترین سرویس ها']),
                ast.literal_eval(
                    row['تاریخ استفاده ی پر بازدید ترین سرویس ها']
                ),
                ast.literal_eval(row['کم بازدید ترین سرویس ها']),
                ast.literal_eval(
                    row['تاریخ استفاده ی کم بازدید ترین سرویس ها']
                ),
                ast.literal_eval(row['تاریخ بازدید سایت']),
                ast.literal_eval(row['اطلاعات کاربر']),
                ast.literal_eval(row['نام ستون های اطلاعات کاربری'])
            ]

            model.add_array(data)

        if not model.data:
            flash('فایل CSV خالی است.')
            return redirect(
                f'/dashboard/service?password={session["userinfo"]["password"]}'
            )

        model.create_df()

        res = model.calculate()

    except Exception as e:
        print(e)
        flash('ساختار فایل CSV نامعتبر است.')
        return redirect(
            f'/dashboard/service?password={session["userinfo"]["password"]}'
        )

    return render_template(
        'dashboard/result.html',
        user=user,
        result=res
    )