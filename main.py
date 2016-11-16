from utils import log
from flask import Flask
from flask import request
from flask import render_template
from todo import main as todo_routes
from user import main as user_routes
from weibo import main as weibo_routes
from chatroom import main as chatroom_routes
import redis


def redis_run():
    red = redis.Redis(host='localhost', port=6379, db=0)
    log('redis', red)
    return red

app = Flask(__name__)
# 设置 secret_key 来使用 flask 自带的 session
# 这个字符串随便你设置什么内容都可以
app.secret_key = 'random string'
# 这一行是套路
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

"""
在 flask 中，模块化路由的功能由 蓝图（Blueprints）提供
蓝图可以拥有自己的静态资源路径、模板路径（现在还没涉及）
用法如下
"""
# 注册蓝图
# 有一个 url_prefix 可以用来给蓝图中的每个路由加一个前缀
app.register_blueprint(todo_routes,
                       url_prefix='/todo')

app.register_blueprint(weibo_routes,
                       url_prefix='/weibo')

app.register_blueprint(user_routes,
                       url_prefix='/user')

app.register_blueprint(chatroom_routes,
                       url_prefix='/chatroom')


@app.route('/')
def index():
    # log('user agen:', request.headers.get('User-Agent'))
    if 'MicroMessenger' in request.headers.get('User-Agent'):
        return '<h1 align="center"  style="color:black ; font-size:120px">请按右上角三个点↗↗↗<br>选自带浏览器打开</h1><br>'' \
        ''<h1 align="center"  style="color:red ; font-size:300px">F*CK 腾讯</h1> <br> '

    elif 'yes' == request.args.get('nsukey', 'yes'):
        # log('request.headers', request.args)
        return render_template('codee.html')

    return '<h1 align="center"  style="color:black ; font-size:100px">请手动输入网址："codee.cc"</h1><br> '


@app.errorhandler(404)
def error404(e):
    return render_template('404.html')


# 运行代码
# 默认端口是 5000
if __name__ == '__main__':
    # app.run(debug=True)
    # debug 模式可以自动加载你对代码的变动, 所以不用重启程序
    # host 参数指定为 '0.0.0.0' 可以让别的机器访问你的代码
    config = dict(
        debug=True,
        host='0.0.0.0',
        port=80,
    )
    # red = redis.Redis(host='localhost', port=6379, db=0)
    # log('redis', red)
    app.run(**config)
    # app.run() 开始运行服务器
    # 所以你访问下面的网址就可以打开网站了
    # http://127.0.0.1:2000/
