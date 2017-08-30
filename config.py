#encoding:utf8

import os
from flask_login import login_manager
class Config:
	#连接mysql的连接，应该放在本地的环境变量里！
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:python123@localhost:3306/test'
    #自动保存开启
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    HOST = '0.0.0.0'
    PORT = 80
    DEBUG = True
    SECRET_KEY = 'python123'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
