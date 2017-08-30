#encoding:utf8
from flask import render_template, request, g, abort, redirect, url_for
from ..main import main
from flask_login import login_user, current_user
from ..models import db, Answer, Like_answer, Question, Comment_answer, User
import collections
import sqlalchemy
from flask_login import login_required



@main.route('/')
@main.route('/index')
def index():
    ''' 主页
        这里将所有的答案取出并按赞序排序（一般不建议将表中数据取出，
    后面可以设计只显示与用户相关的答案）
    '''
    answers = Answer.query.all()
    answers.sort(key=lambda i:i.like_counter,reverse=True)
    return render_template('main/index.html', answers = answers)

@main.route('/question/<question_id>')
def question(question_id):
    '''问题视图
       显示某问题的详细信息，包括关注数、提问者、提问时间、它的答案、答案的评论
    '''
    #通过question的id查询出question
    question = Question.query.filter_by(id=int(question_id)).first()
    #如果问题不存在，返回404页面
    if not question:
        abort(404)
    #获取问题的所有答案，并按赞序排序
    answers = question.answer_sort_by_like()
    return render_template('main/question.html', question = question, answers=answers)

    


@main.route('/ask', methods=['GET', 'POST'])
@login_required
def ask():
    '''提问视图
    提供一个输入问题的表单
    '''
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_question = Question(title=title, description=description, user_id=current_user.id)
        db.session.add(new_question)

        db.session.commit()
        return redirect(url_for('main.question_list',ask_or_atten='ask',user_id=current_user.id))
    return render_template('main/ask.html')

@main.route('/search', methods=['GET', 'POST'])
def search():
    '''搜索视图，可在数据库中搜索问题的标题、答案的内容、用户的名字，使用%str%正则表达式'''
    res_question,res_answer,res_user = ([],[],[])
    if request.method == "POST":
        keyword = request.form['keyword']
        res_question = Question.query.filter(Question.title.like('%'+str(keyword)+'%')).all()
        res_answer = Answer.query.filter(Answer.content.like('%'+str(keyword)+'%')).all()
        res_user = User.query.filter(User.name.like('%'+str(keyword)+'%')).all()
    return render_template('main/search.html',res_question = res_question,
                                              res_answer = res_answer,
                                              res_user = res_user)



@main.route('/dynamic')
@login_required
def dynamic():
    '''用户的动态，显示用户的关注者最新（从此用户上次登录的时间点开始到现在）回答过的、赞过的答案
    '''
    pass

@main.route('/question_list/<ask_or_atten>/<user_id>')
def question_list(ask_or_atten,user_id):
    '''显示用户提问的或者关注的问题的列表'''
    user = User.query.get(int(user_id))
    if ask_or_atten == 'ask':
        res = Question.query.filter_by(user_id=int(user_id)) 
    if ask_or_atten == 'atten':
        res = user.counter_question_attention()[0]
    return render_template('main/question_list.html', res=res, user=user)




