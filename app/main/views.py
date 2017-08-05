#encoding:utf8
from flask import render_template, request
from ..main import main
from flask_login import login_user

@main.route('/')
def index():
    return render_template('base.html')



