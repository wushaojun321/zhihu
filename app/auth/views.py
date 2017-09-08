#encoding:utf8
from flask import render_template, request, url_for, redirect, flash, g
from ..auth import auth
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User
from .. import db




@auth.route('/login', methods=['POST', 'GET'])
def login():
    '''用户登录视图'''
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        #判断用户输入的email是否存在，密码是否一致
        if user is not None and user.password == request.form['password']:
            #此处为flask_login提供的一个接口，执行它，用户的登录状态将会保存在session里
            login_user(user, request.form.get('remember_me', False))
            flash('登录成功！')
            #登录成功后重定向到主页
            return redirect(url_for('main.index'))
        flash('登录失败，请检查账号或者密码是否正确！')
        #登录失败则以GET方式重定向到这个视图
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html')

@auth.route('/reg', methods=['POST', 'GET'])
def reg():
    '''注册视图，以GET形式访问时提供注册表单
    以POST时，则进行注册
    '''
    if request.method == 'POST':
        #判断email是否存在
        if User.query.filter_by(email=request.form['email']).first():
            flash('邮箱已存在！')
        #判断密码长度
        elif len(request.form['password']) <= 6:
            flash('密码长度不够！')
        #判断用户名（username）是否存在
        elif User.query.filter_by(username=request.form['username']).first():
            flash('用户名已存在！')
        #判断两侧密码是否一致，此功能最好在前端实现
        elif request.form['password'] != request.form['confirm_password']:
            flash('两次密码不一致！')
        elif request.form['name'] == '' or User.query.filter_by(name=request.form['name']).first():
            flash('姓名为空或者已经存在！')
        else:
            new_user = User(email=request.form['email'],
                            username=request.form['username'],
                            name=request.form['name'],
                            password=request.form['password'])
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('注册成功！')
                return redirect(url_for('auth.login'))
            except:
                flash('数据库出状况了！')
    return render_template('auth/reg.html')

@auth.route('/logout', methods=['GET'])
def logout():
    '''登出视图函数，执行flask_login内的logout_user函数,将用户登录状态从session里删除'''
    logout_user()
    #并重定向到主页
    return redirect(url_for('main.index'))

@auth.route('/secret', methods=['GET'])
@login_required
def secret():
    '''用来测试是否登录成功，后面删掉'''
    return '<h1>你不该来这！</h1>'

@auth.route('/change_account/<user_id>', methods=['GET', 'POST'])
@login_required
def change_account(user_id):
    '''用来展示用户信息的表单：用户名、姓名、邮箱、TA关注的问题、TA点过的赞、TA的问题、TA的答案
    表单中的密码、姓名可以修改，用户POST姓名、密码后跳转至视图change_password，完成相关资料的修改'''
    user_query = User.query.get(int(user_id))
    return render_template('auth/account.html', user_query=user_query)

@auth.route('/change_password', methods=['POST'])
def change_password():
    '''修改密码和姓名的视图，不可以用GET方式'''
    user_query = User.query.get(int(current_user.id))
    if request.method == 'POST':
        #判断表单内的name是否为空
        if request.form['name'] != '':
            #判断修改后的name是否与原name一样
            if user_query.name != request.form['name']:
                #修改name
                user_query.name = request.form['name']
                message1='名字修改成功！'
            else:
                message1='名字一样，不需要改！'
        #判断表单内的两个密码是否一致
        if request.form['password'] == request.form['confirm_password']:
            #如果一致是否为空
            if request.form['password'] != '':
                #以上都满足，修改密码
                user_query.password = request.form['password']
                message2='密码修改成功！'
            else:
                message2='密码为空，修改失败！'
        else:
            message1='名字为空，修改失败！'
        db.session.commit()
        flash(message1+message2)
        return redirect(url_for('auth.change_account', user_id=user_query.id))

@auth.route('/attention_user/<followed_id>')
def attention_user(followed_id):
    if current_user.attention_user(followed_id):
        flash('关注成功！')
    else:
        flash('关注失败！')
    return redirect(request.referrer)

@auth.route('/cancel_attention_user/<followed_id>')
def cancel_attention_user(followed_id):
    if current_user.cancel_attention_user(followed_id):
        flash('取消关注成功！')
    else:
        flash('取消关注失败！')
    return redirect(request.referrer)