#encoding:utf8
from flask_sqlalchemy import SQLAlchemy
from . import db
from flask_login import UserMixin
from . import login_manager
import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(80), unique=True)
    reg_time = db.Column(db.DateTime, default = datetime.datetime.now)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), default=2)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))