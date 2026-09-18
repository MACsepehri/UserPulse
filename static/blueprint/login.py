from flask import Blueprint, render_template, abort, redirect, request, session

login_bp = Blueprint('auth', __name__,url_prefix='/auth')

@login_bp.route('/')
def login():
    if not session:
        session['login'] = True
    if session['login']:
        return redirect('/dashboard')
    mode = request.args.get('mode', '')
    if mode not in ('login', 'register'):
        abort(404)
    return render_template('page/auth.html',mode=mode)