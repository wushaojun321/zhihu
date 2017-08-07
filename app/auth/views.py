#encoding:utf8
from flask import render_template, request, url_for, redirect, flash
from ..auth import auth
from flask_login import login_user, logout_user, login_required
from ..models import User
from .. import db

@auth.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user is not None and user.password == request.form['password']:
            login_user(user, request.form.get('remember_me', False))
            flash('seccess!')
            return render_template('main/index.html')
        flash('failed!')
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html')

@auth.route('/reg', methods=['POST', 'GET'])
def reg():
    error = ''
    if request.method == 'POST':
        if User.query.filter_by(email=request.form['email']).first():
            error = '邮箱已存在！'
        elif len(request.form['username']) < 9:
            error = '你的密码像你的JJ一样短！'
        elif User.query.filter_by(username=request.form['username']).first():
            error = '用户名已存在！'
        elif request.form['password'] != request.form['confirm_password']:
            error = '两次密码不一致！'
        else:
            new_user = User(email=request.form['email'],
                            username=request.form['username'],
                            password=request.form['password'])
            try:
                db.session.add(new_user)
                db.session.commit()
            except:
                error = '数据库出状况了！'
            if error == '':
                return redirect(url_for('auth.login'))
    return render_template('auth/reg.html', error=error)

@auth.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/secret', methods=['GET'])
@login_required
def secret():
    return '<h1>你不该来这！</h1>'

@auth.route('/change_account', methods=['GET', 'POST'])
@login_required
def change_account():
    return render_template('auth/account.html')

@auth.route('/change_password', methods=['GET', 'POST'])
def change_password():
    return render_template('auth/change_password.html')