from utils import log
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import Blueprint
from flask import abort
from flask import session

from models import User
from models import Weibo
from models import Comment
import copy

# 创建一个 蓝图对象 并且路由定义在蓝图对象中
# 然后在 flask 主代码中「注册蓝图」来使用
# 第一个参数是蓝图的名字，第二个参数是套路
main = Blueprint('weibo', __name__)


def current_user():
    uid = session.get('user_id')
    if uid is not None:
        u = User.query.get(uid)
        return u


def show_weibo():
    pass


@main.route('/')
def index():
    u = current_user()
    # 这里是游客查看全部weibo
    if u is None:
        # 这里是全部用户的索引
        user_list = User.query.all()
        all_weibo = Weibo.query.filter_by(hidden=0).all()
        fix_all_weibo = User.change_uid_to_uname(User, all_weibo)
        # fix_all_weibo = copy.deepcopy(all_weibo)
        # for ws in fix_all_weibo:
        #     wu = User.query.filter_by(id=ws.user_id).first()
        #     ws.user_id = wu.username
        fix_ws_comment = Weibo.inser_comment_to_weibo(Weibo, fix_all_weibo)
        return render_template('timeline.html', users=user_list, weibos=fix_ws_comment)
    else:
        # return redirect('/weibo/timeline/{}'.format(u.username))
        # 上面是直接写网址，下面是url_for带参数的写法
        return redirect(url_for('.timeline_view', username=u.username))


@main.route('/timeline/<username>')
def timeline_view(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        # abort(404)
        return '查无此人'
    else:
        # 这里是全部用户的索引
        us = User.query.all()
        # 这里是自己查看自己的weibo
        # ws = Weibo.query.filter_by(user_id=u.id).all()
        ws = u.weibos()
        # 这里把ID显示成用户名
        fix_ws = User.change_uid_to_uname(User, ws)
        # fix_ws = copy.deepcopy(ws)
        # for fws in fix_ws:
        #     wu = User.query.filter_by(id=fws.user_id).first()
        #     fws.user_id = wu.username
        # 下面是把当前微博的comment_list动态添加进每个weibo字典里
        #     fws.cs = Comment.query.filter_by(weibo_id=fws.id).all()   (旧)下面是抽出来放到weibo model里了
        fix_ws_comment = Weibo.inser_comment_to_weibo(Weibo, fix_ws)
        return render_template('timeline.html', users=us, weibos=fix_ws_comment)


@main.route('/add', methods=['POST'])
def add():
    u = current_user()
    if u is None:
        return render_template('user_login.html')
        # abort(404)
    else:
        form = request.form
        w = Weibo(form)
        w.user_id = u.id
        w.save()
        return redirect(url_for('.timeline_view', username=u.username))


@main.route('/comment/add', methods=['POST'])
def comment():
    u = current_user()
    if u is None:
        # abort(404)
        return render_template('user_login.html')
    else:
        form = request.form
        c = Comment(form)
        c.user_id = u.id
        c.save()
        # 下面两行是从comment一直向上找到微博主的名字来避免评论后跳转到自己的微博
        weibo = Weibo.query.filter_by(id=c.weibo_id).first()
        own = User.query.filter_by(id=weibo.user_id).first()
        return redirect(url_for('.timeline_view', username=own.username))


@main.route('/delete/<int:item_id>')
def delete(item_id):
    u = current_user()
    w = Weibo.query.get(item_id)
    if u is None:
        # abort(404)
        return render_template('user_login.html')
    elif u.id == w.user_id:
        # 删除
        w.hidden = 1
        w.save()
        # t.delete()
    else:
        # abort(404)
        return '不是你的能动吗？'
    # 引用蓝图内部的路由函数的时候，可以省略名字只用 .
    return redirect(url_for('.index'))


@main.route('/comment/delete/<int:item_id>')
def comment_delete(item_id):
    u = current_user()
    w = Comment.query.get(item_id)
    if u is None:
        # abort(404)
        return render_template('user_login.html')
    elif u.id == w.user_id:
        # 删除
        w.hidden = 1
        w.save()
        # t.delete()
    else:
        # abort(404)
        return '不是你的能动吗？'
    # 引用蓝图内部的路由函数的时候，可以省略名字只用 .
    return redirect(url_for('.index'))
