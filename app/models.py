#encoding:utf8
from flask_sqlalchemy import SQLAlchemy
from . import db
from flask_login import UserMixin
from . import login_manager
import datetime
import sqlalchemy

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

class Attention_user(db.Model):
    __tablename__ = 'attention_users'
    attention_time = db.Column(db.DateTime, default=datetime.datetime.now)

    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

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
    followed = db.relationship('Attention_user', foreign_keys=[Attention_user.follower_id],
                                 backref=db.backref('follower', lazy='joined'), lazy='dynamic',
                                 cascade = 'all, delete-orphan')
    follower = db.relationship('Attention_user', foreign_keys=[Attention_user.followed_id],
                                backref=db.backref('followed', lazy='joined'), lazy='dynamic',
                                cascade = 'all, delete-orphan')
    def counter_followed(self):
        res = self.followed.all()
        return res,len(res)
    def counter_follower(self):
        res = self.follower.all()
        return res,len(res)
    def counter_question_attention(self):
        res = Question.query.filter_by(user_id=self.id).all()
        return res,len(res)
    def counter_like_answer(self):
        b = Like_answer.query.filter_by(user_id=self.id).all()
        _L = [i.answer_id for i in b]
        res = Answer.query.filter(Answer.id.in_(tuple(_L))).all()
        return res, len(res) 


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

    def answer_sort_by_like(self):
        res = Answer.query.filter_by(question_id=self.id)
        _L = [(i.id, i.get_like_counter()) for i in res]
        _L.sort(key=lambda i:i[1], reverse=True)
        _T = tuple(i[0] for i in _L)
        return res.order_by(sqlalchemy.sql.expression.func.field(Answer.id,*_T))

    def get_attention_counter(self):
        res = Attention_question.query.filter_by(question_id=self.id).all()
        return len(res)

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

    def get_like_counter(self):
        res = len(Like_answer.query.filter_by(answer_id=self.id).all())
        return res

    def get_comment_answer(self):
        res = Comment_answer.query.filter_by(answer_id=self.id)
        res_counter = len(res.all())
        return res,res_counter



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

