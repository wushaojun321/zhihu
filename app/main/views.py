#encoding:utf8
from flask import render_template, request
from ..main import main
from flask_login import login_user

@main.route('/')
@main.route('/index')
def index():
    return render_template('main/index.html')

@main.route('/ask')
def ask():
	return render_template('main/ask.html')

@main.route('/search', methods=['GET', 'POST'])
def search():
	return render_template('main/search.html')

@main.route('/write_text', methods=['GET', 'POST'])
def write_text():
	return render_template('main/write_text.html')

@main.route('/dynamic')
def dynamic():
	return render_template('main/dynamic.html')



