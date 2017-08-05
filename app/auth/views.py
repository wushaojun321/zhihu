#encoding:utf8
from flask import render_template, request, url_for, redirect
from ..auth import auth
from flask_login import login_user, logout_user, login_required
from ..models import User

@auth.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is not None and user.password == request.form['password']:
            return 'success logined！'
        return '<h1>login failed!</h1>'
    return render_template('auth/login.html')

@auth.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/secret', methods=['GET'])
@login_required
def secret():
    return '<h1>你不该来这！</h1>'