# #encoding:utf8

from faker import Factory
import datetime, time


faker_china = Factory.create('zh_CN')
faker_english = Factory.create()
class Isert_data():
    def __init__(self, models, db):
        self.models = models
        self.db = db

    def insert_role(self):
        adminisitor = self.models.Role(name = 'Adminisitor')
        self.db.session.add(adminisitor)
        super_user = self.models.Role(name = 'Super_user')
        self.db.session.add(super_user)
        user = self.models.Role(name = 'User')
        self.db.session.add(user)

    def insert_user(self):
        username = faker_english.name()
        name = faker_china.name()
        email = faker_english.email()
        password = faker_english.password()
        reg_time = datetime.datetime.now() + datetime.timedelta(hours=120)
        new_user = self.models.User(username=username, email=email,name=name, password=password)
        self.db.session.add(new_user)

    def insert_question(self, count_user):
        title = faker_china.text()[0:20] + '？'
        description = faker_china.text()
        user_id = faker_english.random_int(1,count_user)
        new_question = self.models.Question(title=title, 
                                        description=description, user_id=user_id)
        self.db.session.add(new_question)

    def insert_answer(self, user_id, question_id):
        content = faker_china.text()
        new_answer = self.models.Answer(question_id=question_id, user_id=user_id, 
                                        content=content)
        self.db.session.add(new_answer)


    def insert_attention_question(self, user_id, question_id):
        new_attention_question = self.models.Attention_question(user_id=user_id,
                                                                question_id=question_id)
        self.db.session.add(new_attention_question)

    def insert_comment_answer(self, user_id, answer_id):
        content = faker_china.text()[0:10]
        new_comment_answer = self.models.Comment_answer(content=content,user_id=user_id,
                                                        answer_id=answer_id)
        self.db.session.add(new_comment_answer)

    def insert_like_answer(self, user_id, answer_id):
        new_like_answer = self.models.Like_answer(user_id=user_id,answer_id=answer_id)
        self.db.session.add(new_like_answer)

def go(modes, db):
    i = Isert_data(modes, db)

    i.insert_role()
    try: 
        i.db.session.commit()
        print '插入Role  seccess！'
    except:
        print '插入Role  failed！'


    if len(i.models.Role.query.all()) == 0:
        print 'Role里面没有数据！插入User  failed！'
        return
    for x in range(500):
        i.insert_user()
    try: 
        i.db.session.commit()
        print '插入User  seccess！'
    except:
        print '插入User  failed！'
        return
    #插入question
    count_user = len(i.models.User.query.all())
    if count_user == 0:
        print '没有用户存在，无法插入问题！'
        return
    for x in range(800):
        i.insert_question(count_user)
    try: 
        i.db.session.commit()
        print '插入Question  seccess！'
    except:
        print '插入Question  failed！'
        return
    #插入答案
    def gen_insert_answer(count_user, count_question):
        L = []
        for i in range (5000):
            L.append((faker_english.random_int(1,count_user), 
                                faker_english.random_int(1,count_question)))
        L = list(set(L))
        L1 = []
        d = {i[0] for i in L}
        for i in L:
            if i[0] in d:
                L1.append(i)
                d.remove(i[0])
        return L1
    count_question = len(i.models.Question.query.all())
    if count_question == 0 or count_user == 0:
        print '没有问题或者用户，插不进去答案啊！'
        return
    L = gen_insert_answer(count_user, count_question)
    for x in L:
        i.insert_answer(user_id=x[0], question_id=x[1])
    try: 
        i.db.session.commit()
        print '插入Answer  seccess！'
    except:
        print '插入Answer  failed！'
        return    

    #插入关注问题
    L = gen_insert_answer(count_user, count_question)
    for x in L:
        i.insert_attention_question(user_id=x[0], question_id=x[1])
    try: 
        i.db.session.commit()
        print '插入关注问题  seccess！'
    except:
        print '插入关注问题  failed！'
        return
    count_answer = len(i.models.Answer.query.all())
    #插入答案评论
    if count_answer == 0:
        print '没有答案，插不了答案的评论！'
        return
    L = gen_insert_answer(count_user, count_answer)
    for x in L:
        i.insert_comment_answer(user_id=x[0], answer_id=x[1])
    try: 
        i.db.session.commit()
        print '插入问题评论  seccess！'
    except:
        print '插入问题评论  failed！'
        return

    #插入答案的赞
    L = gen_insert_answer(count_user, count_answer)
    for x in L:
        i.insert_like_answer(user_id=x[0], answer_id=x[1])
    try: 
        i.db.session.commit()
        print '插入答案的赞  seccess！'
    except:
        print '插入答案的赞  failed！'
        return







