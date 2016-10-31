from utils import log
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import Blueprint
from flask import abort
from flask import session

from models import User

# 创建一个 蓝图对象 并且路由定义在蓝图对象中
# 然后在 flask 主代码中「注册蓝图」来使用
# 第一个参数是蓝图的名字，第二个参数是套路
main = Blueprint('user', __name__)


def current_user():
    # 在http头中的cookie：user_id,get到session加密后的user_id
    uid = session.get('user_id')
    if uid is not None:
        # 在User.query找加密后的user_id，得到真正的user
        u = User.query.get(uid)
        return u


@main.route('/')
def login_view():
    u = current_user()
    if u is not None:
        return redirect(url_for('.profile'))
    # 直接路径跳转用redirect('/路径')，根据函数名跳转用redirect(url_for('蓝图.路由函数'))
    # 返回template网页用render_template('name.html')
    return render_template('user_login.html')


@main.route('/register', methods=['POST'])
def register():
    # request.form 是 flask 保存 POST 请求的表单数据的属性（用flask自定义字典）(post请求的form保存在在httpbody里)
    form = request.form
    u = User(form)
    if u.valid():
        u.save()
        return '返回登陆一下吧'
    else:
        return '太短啦'
        # abort(400)
    # 蓝图中的 url_for 需要加上蓝图的名字，这里是 user
    # return redirect(url_for('.login_view'))


@main.route('/login', methods=['POST'])
def login():
    form = request.form
    u = User(form)
    # 检查 u 是否存在于数据库中并且 密码用户 都验证合格
    # filter_by
    user = User.query.filter_by(username=u.username).first()
    if user is not None and user.validate_login(u):
        # 设置cookie，session['key'] = 'value'
        session['user_id'] = user.id
    else:
        return '登陆不成功，检查一下啊'
    # 蓝图中的 url_for 需要加上蓝图的名字，这里是 user
    return redirect(url_for('.login_view'))


@main.route('/update', methods=['POST'])
def update():
    u = current_user()
    password = request.form.get('password', '123')
    if u.change_password(password):
        pass
    else:
        return '用户密码修改失败'
    return render_template('profile.html', user=u)


@main.route('/profile', methods=['GET'])
def profile():
    u = current_user()
    if u is not None:
        return render_template('profile.html', user=u)
    else:
        abort(401)


@main.route('/out')
def out():
    session['user_id'] = 'userout'
    return redirect(url_for('.login_view'))

