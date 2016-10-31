from utils import log
from utils import now
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import time
import copy
import json

# 以下都是套路
app = Flask(__name__)
app.secret_key = 'secret key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# 指定数据库的路径
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///codee.db'

db = SQLAlchemy(app)


class ModelHelper(object):
    def __repr__(self):
        """
        __repr__ 是一个魔法方法
        简单来说, 它的作用是得到类的 字符串表达 形式
        比如 print(u) 实际上是 print(u.__repr__())
        """
        classname = self.__class__.__name__
        properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{} \n>\n'.format(classname, s)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


# 定义一个 Model，继承自 db.Model
class Todo(db.Model, ModelHelper):
    __tablename__ = 'todos'
    # 下面是字段定义
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String())
    created_time = db.Column(db.Integer, default=0)
    hidden = db.Column(db.Integer, default=0)
    # 定义关系
    user_id = db.Column(db.Integer)

    def __init__(self, form):
        self.task = form.get('task', 'None')
        self.created_time = now()
        self.hidden = 0

    def valid(self):
        return len(self.task) > 0


# 定义一个 Model，继承自 db.Model
class Weibo(db.Model, ModelHelper):
    __tablename__ = 'weibos'
    # 下面是字段定义
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String())
    created_time = db.Column(db.Integer, default=0)
    hidden = db.Column(db.Integer, default=0)
    # 定义关系
    user_id = db.Column(db.Integer)

    def __init__(self, form):
        self.content = form.get('content', '')
        self.created_time = now()
        self.hidden = 0

        # 下面纯粹是为了动态加入每条微博的评论，顺便把comment里的id换成用户名显示

    def inser_comment_to_weibo(self, weibo_list):
        for w in weibo_list:
            w.cs = Comment.query.filter_by(weibo_id=w.id, hidden=0).all()
            w.cs = User.change_uid_to_uname(User, w.cs)
        return weibo_list


class Comment(db.Model, ModelHelper):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String())
    created_time = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer)
    weibo_id = db.Column(db.Integer)
    hidden = db.Column(db.Integer, default=0)

    def __init__(self, form):
        self.content = form.get('content', '')
        self.weibo_id = int(form.get('weibo_id', ''))
        self.created_time = now()
        self.hidden = 0

    def json(self):
        d = {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'weibo_id': self.weibo_id,
            'created_time': self.created_time,
            'hidden': self.hidden,
        }
        return json.dumps(d, ensure_ascii=False)


class User(db.Model, ModelHelper):
    __tablename__ = 'users'
    # 下面是字段定义
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    password = db.Column(db.String())
    created_time = db.Column(db.Integer, default=0)

    def __init__(self, form):
        self.username = form.get('username', '')
        self.password = form.get('password', '')
        self.created_time = now()

    def weibos(self):
        ws = Weibo.query.filter_by(user_id=self.id, hidden=0).all()
        return ws

    def todos(self):
        ts = Todo.query.folter_by(user_id=self.id).all()
        return ts

    def change_uid_to_uname(self, item_list):
        fix_item_list = copy.deepcopy(item_list)
        for i in fix_item_list:
            if i.user_id is None:
                i.user_id = '游客'
            else:
                u = self.query.filter_by(id=i.user_id).first()
                i.user_id = u.username
                # i.cs = Comment.query.filter_by(weibo_id=i.id).all()
        return fix_item_list

    def valid(self):
        return len(self.username) > 2 and len(self.password) > 2

    def validate_login(self, u):
        return u.username == self.username and u.password == self.password

    def change_password(self, password):
        if len(password) > 2:
            self.password = password
            self.save()
            return True
        else:
            return False


def init_db():
    # 先 drop_all 删除所有数据库中的表
    # 再 create_all 创建所有的表
    db.drop_all()
    db.create_all()
    print('rebuild database')


if __name__ == '__main__':
    init_db()
    # """
    # select * from users where id=1
    #
    # update users set password='pwd' where id=1
    #
    # SELECT
    #     todos.id AS todos_id,
    #     todos.task AS todos_task,
    #     todos.created_time AS todos_created_time,
    #     todos.user_id AS todos_user_id
    # FROM
    #     todos
    # WHERE
    #     todos.user_id = :user_id_1
    # """
    # u = User.query.get(1)
    # # u.password = 'pwd'
    # # u.save()
    # print('sql', Todo.query.filter_by(user_id=u.id))
    # ts = Todo.query.filter_by(user_id=u.id).all()
    # print('todos', ts)
