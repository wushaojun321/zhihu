#encoding:utf8

import os
from flask_login import login_manager
class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:python123@localhost:3306/test'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    HOST = '0.0.0.0'
    PORT = 80
    DEBUG = True
    SECRET_KEY = 'python123'
    LOGIN_VIEW = 'login'
