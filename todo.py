from utils import log
import copy
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import Blueprint
from flask import abort
from flask import session

from models import Todo
from models import User

# 创建一个 蓝图对象 并且路由定义在蓝图对象中
# 然后在 flask 主代码中「注册蓝图」来使用
# 第一个参数是蓝图的名字，第二个参数是套路
main = Blueprint('todo', __name__)


# 这个是获取当前浏览器登录的用户
def current_user():
    uid = session.get('user_id')
    if uid is not None:
        u = User.query.get(uid)
        return u


@main.route('/')
def index():
    # 查找所有的 todo 并返回
    todo_list = Todo.query.filter_by(hidden=0).all()
    fix_todo_list = User.change_uid_to_uname(User, todo_list)
    # fix_todo_list = copy.deepcopy(todo_list)
    # for t in fix_todo_list:
    #     if t.user_id is None:
    #         t.user_id = '游客'
    #     else:
    #         tu = User.query.filter_by(id=t.user_id).first()
    #         t.user_id = tu.username
    return render_template('todo_index.html', todos=fix_todo_list)


@main.route('/add', methods=['POST'])
def add():
    u = current_user()
    form = request.form
    t = Todo(form)
    if u is None:
        t.save()
    else:
        t.user_id = u.id
        t.save()
    return redirect(url_for('todo.index'))


@main.route('/edit/<int:todo_id>')
def edit(todo_id):
    """
    <int:todo_id> 的方式可以匹配一个 int 类型
    int 指定了它的类型，省略的话参数中的 todo_id 就是 str 类型

    这个概念叫做 动态路由
    意思是这个路由函数可以匹配一系列不同的路由

    动态路由是现在流行的路由设计方案
    """
    # 通过 id 查询 todo 并返回
    u = current_user()
    t = Todo.query.get(todo_id)
    log('/edit/<int:todo_id>', t)
    if u is None:
        if t.user_id is None:
            return render_template('todo_edit.html', t=t)
            # t.hidden = 1
            # t.save()
        else:
            # abort(404)
            return '不是你的能动吗？'
    elif u.id == t.user_id:
        return render_template('todo_edit.html')
        # t.hidden = 1
        # t.save()
        # t.delete()
    else:
        # abort(404)
        return '不是你的能动吗？'


@main.route('/update/<int:todo_id>', methods=['POST'])
def update(todo_id):
    """
    <int:todo_id> 的方式可以匹配一个 int 类型
    int 指定了它的类型，省略的话参数中的 todo_id 就是 str 类型

    这个概念叫做 动态路由
    意思是这个路由函数可以匹配一系列不同的路由

    动态路由是现在流行的路由设计方案
    """
    # 通过 id 查询 todo 并返回
    u = current_user()
    t = Todo.query.get(todo_id)
    if u is None:
        if t.user_id is None:
            t.task = request.form.get('todo_task')
            # t.hidden = 1
            t.save()
        else:
            # abort(404)
            return '不是你的能动吗？'
    elif u.id == t.user_id:
        t.task = request.form.get('todo_task')
        # t.hidden = 1
        t.save()
        # t.delete()
    else:
        # abort(404)
        return '不是你的能动吗？'
    return redirect(url_for('.index'))


@main.route('/delete/<int:todo_id>')
def delete(todo_id):
    """
    <int:todo_id> 的方式可以匹配一个 int 类型
    int 指定了它的类型，省略的话参数中的 todo_id 就是 str 类型

    这个概念叫做 动态路由
    意思是这个路由函数可以匹配一系列不同的路由

    动态路由是现在流行的路由设计方案
    """
    # 通过 id 查询 todo 并返回
    u = current_user()
    t = Todo.query.get(todo_id)
    if u is None:
        if t.user_id is None:
            t.hidden = 1
            t.save()
        else:
            # abort(404)
            return '不是你的能动吗？'
    elif u.id == t.user_id:
        # 删除
        t.hidden = 1
        t.save()
        # t.delete()
    else:
        # abort(404)
        return '不是你的能动吗？'
    # 引用蓝图内部的路由函数的时候，可以省略名字只用 .
    return redirect(url_for('.index'))
