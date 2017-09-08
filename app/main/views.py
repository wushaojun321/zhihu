#encoding:utf8
from flask import render_template, request, g, abort, redirect, url_for, flash
from ..main import main
from flask_login import login_user, current_user
from ..models import db, Answer, Like_answer, Question, Comment_answer, User, Attention_question
import collections
import sqlalchemy
from flask_login import login_required



@main.route('/')
@main.route('/index')
def index():
    ''' 主页
        调用Answer的静态方法，获取赞数最多的答案
    '''
    answers = Answer.get_popular_answer()
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

@main.route('/submit_comment/<answer_id>/<question_id>', methods=['POST'])
@login_required
def submit_comment(answer_id, question_id):
    '''提交答案的评论的视图函数，只能用POST请求访问，作为一个跳板，不论评论成功还是失败
    都重定向到question视图，返回之前的问题详情页面'''
    comment_content = request.form.get('comment_content',None)
    if comment_content is not None:
        new_comment = Comment_answer(user_id=current_user.id,answer_id=answer_id,
                                     content=request.form['comment_content'])
        answer = Answer.query.get(answer_id)
        answer.comment_counter = answer.comment_counter + 1
        try:
            db.session.add(new_comment)
            db.session.add(answer)
            db.session.commit()
            flash("评论成功！")
        except:
            flash("数据库原因，评论失败！")

        return redirect(url_for('main.question',question_id=question_id))

@main.route('/submit_answer/<question_id>', methods=['POST'])
def submit_answer(question_id):
    '''提交问题的答案的视图函数,只能用POST请求访问，作为一个跳板，不论回答成功还是失败
    都重定向到question视图，返回之前的问题详情页面'''
    answer_content = request.form.get('answer_content',None)
    if answer_content is not None:
        new_answer = Answer(content=answer_content,user_id=current_user.id,
                            question_id=question_id)
        try:
            db.session.add(new_answer)
            db.session.commit()
            flash("评论成功！")
        except:
            flash("数据库原因，评论失败！")
    return redirect(url_for('main.question',question_id=question_id))

@main.route('/attention_question/<question_id>')
@login_required
def attention_question(question_id):
    '''传入question_id，查询登录的用户是否关注了此问题，若关注，则取消，若未，则关注'''
    _attention_question = Attention_question(user_id=current_user.id,question_id=question_id)
    db.session.add(_attention_question)
    try:
        db.session.commit()
        flash('关注成功！')
    except Exception as e:
        flash('关注失败（%s）' % e)
    if Question.update_attention_counter(question_id,'plus'):
        flash('更新此问题关注的总数成功！')
    else:
        flash('更新此问题关注的总数失败！')
    return redirect(request.referrer)   

@main.route('/cancel_attention_question/<question_id>')
@login_required
def cancel_attention_question(question_id):
    '''传入question_id，查询登录的用户是否关注了此问题，若关注，则取消，若未，则关注'''
    _attention_question = Attention_question.query.filter_by(
                    user_id=current_user.id,question_id=question_id).first()
    db.session.delete(_attention_question)
    try:
        db.session.commit()
        flash('取消关注成功！')

    except Exception as e:
        flash('取消关注失败（%s）' % e)
    if Question.update_attention_counter(question_id,'less'):
        flash('更新此问题关注的总数成功！')
    else:
        flash('更新此问题关注的总数失败！')

    return redirect(request.referrer)     

@main.route('/like_answer/<answer_id>')
@login_required
def like_answer(answer_id):
    '''传入answer_id，加上当前用户，在数据表Like_answer中插入一行,
    并在answer的like_counter中相应位置+1,从而实现点赞功能'''
    _like_answer = Like_answer(user_id=current_user.id,answer_id=int(answer_id))
    db.session.add(_like_answer)
    try:
        db.session.commit()
        flash('点赞成功！')
    except Exception as e:
        flash('点赞失败（%s）'%e)
    if Answer.update_like_counter(answer_id=answer_id,plus_or_less='plus'):
        flash('更新答案的总赞数成功！')
    else:
        flash('更新答案的总赞数失败！')
    if User.update_like_counter(answer_id=answer_id,plus_or_less='plus'):
        flash('更新用户的总赞数成功！')
    else:
        flash('更新用户的总赞数失败！')
    return redirect(request.referrer)

@main.route('/cancel_like_answer/<answer_id>')
@login_required
def cancel_like_answer(answer_id):
    '''传入answer_id，加上当前用户，在数据表Like_answer中插入一行,
    并在answer的like_counter中相应位置+1,从而实现点赞功能'''
    _like_answer = Like_answer.query.filter_by(user_id=current_user.id,answer_id=answer_id).first()
    db.session.delete(_like_answer)
    try:
        db.session.commit()
        flash('取消赞成功！')
    except Exception as e:
        flash('取消赞失败（%s）'%e)
    if Answer.update_like_counter(answer_id=answer_id,plus_or_less='less'):
        flash('更新赞数成功！')
    else:
        flash('更新赞数失败！')
    if User.update_like_counter(answer_id=answer_id,plus_or_less='less'):
        flash('更新用户的总赞数成功！')
    else:
        flash('更新用户的总赞数失败！')
    return redirect(request.referrer)

@main.route('/like_list/<like_or_bylike>/<user_id>')
def like_list(like_or_bylike,user_id):
    '''显示用户赞或者被赞的条目，返回给前端的是Like_answer的查询结果的列表'''
    user = User.query.get(user_id)
    if like_or_bylike == 'like':    
        res = user.counter_like_answer()
    if like_or_bylike == 'bylike':
        res = user.counter_bylike()
    return render_template('main/like_list.html',res=res,user=user,like_or_bylike=like_or_bylike)

@main.route('/answers_list/<user_id>')
def answers_list(user_id):
    user = User.query.get(user_id)
    answers = user.answer_asked()
    return render_template('main/answers_list.html',res=answers,user=user)












