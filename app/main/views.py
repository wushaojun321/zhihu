#encoding:utf8
from flask import render_template
from ..main import main

@main.route('/asd')
def index():
	return render_template('base.html')