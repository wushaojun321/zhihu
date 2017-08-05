#encoding:utf8
from flask_sqlalchemy import SQLAlchemy
from . import db
from flask_login import UserMixin
from . import login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(320), unique=True)
    password = db.Column(db.String(32), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))