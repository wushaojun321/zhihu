#encoding:utf8
from flask_sqlalchemy import SQLAlchemy
from . import db
from flask_login import UserMixin
from . import login_manager
import datetime
import sqlalchemy

class Role(db.Model):
    '''用户权限：管理员，超管，普通用户'''
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

class Attention_user(db.Model):
    '''为实现用户关注的多对多关系创建的表'''
    __tablename__ = 'attention_users'
    attention_time = db.Column(db.DateTime, default=datetime.datetime.now)

    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

class User(UserMixin, db.Model):
    '''这里为了测试能够顺利插入测试数据，本来应该unique=True的去掉了'''
    __tablename__ = 'users'
    #表的列
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(80))
    reg_time = db.Column(db.DateTime, default = datetime.datetime.now)
    last_login_time = db.Column(db.DateTime)
    #一对多关系中多的一方
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), default=3)
    #一对多关系中一的一方
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
        '''User的方法，返回粉丝列表、粉丝数目'''
        res = self.followed.all()
        return res,len(res)
    def counter_follower(self):
        '''User的方法，返回关注的用户列表、数目'''
        res = self.follower.all()
        return res,len(res)
    def counter_question_attention(self):
        '''User的方法，返回用户关注的问题的列表、数目'''
        b = Attention_question.query.filter_by(user_id=self.id).all()
        _L = [i.question_id for i in b]
        res = Question.query.filter(Question.id.in_(tuple(_L))).all()
        return res,len(res)
    def counter_like_answer(self):
        '''User的方法，返回用户赞过的答案的列表、数目'''
        b = Like_answer.query.filter_by(user_id=self.id).all()
        _L = [i.answer_id for i in b]
        res = Answer.query.filter(Answer.id.in_(tuple(_L))).all()
        return res, len(res) 
    def judge_attention_question(self,question_id):
        res = Attention_question.query.filter_by(user_id=self.id,question_id=question_id).first()
        if res:
            return True
        return False
    def judge_like_answer(self,answer_id):
        res = Like_answer.query.filter_by(user_id=self.id,answer_id=answer_id).first()
        if res:
            return True
        return False


class Question(db.Model):
    '''attention_counter这一列通过调用静态方法insert_attention_counter初始化，后面在插入时
    加一，删除时减一，需要时直接从这一列获取值，而不需重新查询'''
    __tablename__ = 'questions'
    #问题的列
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    add_time = db.Column(db.DateTime, default = datetime.datetime.now)
    attention_counter = db.Column(db.Integer, default=0)
    #一对多中一的一方
    answers = db.relationship('Answer', backref='question', lazy='dynamic')
    attention_questions = db.relationship('Attention_question', backref='question', lazy='dynamic')
    #一对多中多的一方
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def insert_attention_counter():
        '''初始化全部问题的Question.attention_counter的值'''
        _q = Question.query.all()
        for i in _q:
            i.attention_counter = i.get_attention_counter()
            db.session.add(i)
        try:
            db.session.commit()
            return '插入问题的关注数success！'
        except:
            return '插入问题的关注数failed！'

    def answer_sort_by_like(self):
        '''Question的方法，返回此问题按赞序排列过的答案的子查询'''
        res = Answer.query.filter_by(question_id=self.id)\
                                    .order_by(sqlalchemy.desc(Answer.like_counter))
        
        return res

    def get_attention_counter(self):
        '''返回此问题的关注数'''
        res = Attention_question.query.filter_by(question_id=self.id).all()
        return len(res)

    @staticmethod
    def update_attention_counter(question_id, plus_or_less):
        question = Question.query.get(question_id)
        if plus_or_less == 'plus':
            question.attention_counter=question.attention_counter+1
        if plus_or_less == 'less':
            question.attention_counter=question.attention_counter-1
        db.session.add(question)
        try:
            db.session.commit()
            return True
        except:
            return False

class Answer(db.Model):
    '''comment_counter、like_counter这两列通过调用静态方法insert_comment_counter、
    insert_like_counter初始化，后面在插入时加一，删除时减一，需要时直接从这两列获取值，
    而不需重新查询'''
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False) 
    add_time = db.Column(db.DateTime, default = datetime.datetime.now)
    like_counter = db.Column(db.Integer, default=0)
    comment_counter = db.Column(db.Integer, default=0)
    #一对多中一的一方
    comment_answers = db.relationship('Comment_answer', backref='answer', lazy='dynamic')
    like_answers = db.relationship('Like_answer', backref='answer', lazy='dynamic')
    #一对多中多的一方
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))

    @staticmethod
    def insert_comment_counter():
        '''静态方法，调用时将更新所有的答案的Answer.comment_counter的值'''
        _q = Answer.query.all()
        for i in _q:
            i.comment_counter = i.get_comment_answer()[1]
            db.session.add(i)
        try:
            db.session.commit()
            return '插入答案的评论数success！'
        except:
            return '插入答案的评论数failed！'

    @staticmethod
    def insert_like_counter():
        '''静态方法，调用时将更新所有的答案的Answer.like_counter的值'''
        _q = Answer.query.all()
        for i in _q:
            i.like_counter = i.get_like_counter()
            db.session.add(i)
        try:
            db.session.commit()
            return '插入答案的赞数success！'
        except:
            return '插入答案的赞数failed！'

    def get_like_counter(self):
        '''Answer的方法，返回此答案的赞的数目'''
        res = len(Like_answer.query.filter_by(answer_id=self.id).all())
        return res

    def get_comment_answer(self):
        '''Answer的方法，返回此答案的关注的列表、数目'''
        res = Comment_answer.query.filter_by(answer_id=self.id).order_by(Comment_answer.add_time.desc())
        res_counter = len(res.all())
        return res,res_counter
    @staticmethod
    def update_like_counter(answer_id,plus_or_less):
        answer = Answer.query.get(answer_id)
        if plus_or_less == 'plus':
            answer.like_counter = answer.like_counter+1
        if plus_or_less == 'less':
            answer.like_counter = answer.like_counter-1
        db.session.add(answer)
        try:
            db.session.commit()
            return True
        except:
            return False



class Comment_answer(db.Model):
    '''答案的评论，包含答案的id，评论者的id，评论的内容'''
    __tablename__ = 'comment_answers'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False) 
    add_time = db.Column(db.DateTime, default = datetime.datetime.now)
    #一对多中多的一方
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'))

class Attention_question(db.Model):
    '''问题的关注，保存问题的id、关注者的id'''
    __tablename__ = 'attention_questions'
    id = db.Column(db.Integer, primary_key=True)
    attention_time = db.Column(db.DateTime, default = datetime.datetime.now)
    #一对多中多的一方
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))

class Like_answer(db.Model):
    '''答案的赞，保存点赞者的id，答案的id'''
    __tablename__ = 'like_answers'
    id = db.Column(db.Integer, primary_key=True)
    like_time = db.Column(db.DateTime, default=datetime.datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'))



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

