#encoding:utf8
from flask_sqlalchemy import SQLAlchemy
from . import db
from flask_login import UserMixin
from . import login_manager
import datetime

class User(UserMixin, db.Model):
    #这里为了测试能够顺利插入测试数据，本来应该unique=True的去掉了
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(80))
    reg_time = db.Column(db.DateTime, default = datetime.datetime.now)
    last_login_time = db.Column(db.DateTime)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), default=3)

    questions = db.relationship('Question', backref='user', lazy='dynamic')
    answers = db.relationship('Answer', backref='user', lazy='dynamic')
    comment_answers = db.relationship('Comment_answer', backref='user', lazy='dynamic')
    attention_questions = db.relationship('Attention_question', backref='user', lazy='dynamic')
    like_answers = db.relationship('Like_answer', backref='user', lazy='dynamic')



class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

class Question(db.Model):
    #问题
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    add_time = db.Column(db.DateTime, default = datetime.datetime.now)

    answers = db.relationship('Answer', backref='question', lazy='dynamic')
    attention_questions = db.relationship('Attention_question', backref='question', lazy='dynamic')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Answer(db.Model):
    #回答
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False) 
    add_time = db.Column(db.DateTime, default = datetime.datetime.now)

    comment_answers = db.relationship('Comment_answer', backref='answer', lazy='dynamic')
    like_answers = db.relationship('Like_answer', backref='answer', lazy='dynamic')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))

class Comment_answer(db.Model):
    __tablename__ = 'comment_answers'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False) 
    add_time = db.Column(db.DateTime, default = datetime.datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'))

class Attention_question(db.Model):
    __tablename__ = 'attention_questions'
    id = db.Column(db.Integer, primary_key=True)
    attention_time = db.Column(db.DateTime, default = datetime.datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))

class Like_answer(db.Model):
    __tablename__ = 'like_answers'
    id = db.Column(db.Integer, primary_key=True)
    like_time = db.Column(db.DateTime, default=datetime.datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

