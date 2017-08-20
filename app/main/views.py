#encoding:utf8
from flask import render_template, request, g, abort
from ..main import main
from flask_login import login_user, current_user
from ..models import Answer, Like_answer, Question, Comment_answer
import collections
import sqlalchemy



@main.route('/')
@main.route('/index')
def index():

    answers = Answer.query.all()
    answers.sort(key=lambda i:i.get_like_counter(),reverse=True)

    return render_template('main/index.html', answers = answers)

@main.route('/question/<question_id>')
def question(question_id):
    question = Question.query.filter_by(id=int(question_id)).first()
    if not question:
        abort(404)
    answers = Answer.query.filter_by(question_id=question_id)
    if len(answers.all()) != 0:
        d = {answer.id:len(Like_answer.query.filter_by(answer_id=answer.id).all())
                for answer in answers}
        d_item = d.items()
        d_item.sort(key=lambda x:x[1], reverse=True)
        d_answer_id = tuple([i[0] for i in d_item])
        res_answers = answers.order_by(
                    sqlalchemy.sql.expression.func.field(Answer.id,*d_answer_id))
        res_comment = Comment_answer.query.filter(Comment_answer.answer_id.in_(d_answer_id))

    else:
        res_answers = None
        d = None
        res_comment = None

    return render_template('main/question.html', question = question, res_answers=res_answers,
                            d=d, res_comment=res_comment)

    


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



