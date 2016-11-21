import flask
from flask import request
import redis
import time
import json
from utils import log
from flask import render_template
from flask import redirect
from flask import url_for
from flask import Blueprint
from flask import abort
from flask import session
from models import User



'''
# 使用 gunicorn 启动 main:app(文件名:flsak名) -b 设置host和portgunicorn --worker-class=gevent -t 9999 main:app -b 0.0.0.0:80
# 开启 debug 输出
gunicorn --log-level debug --worker-class=gevent -t 999 redis_chat81:app
# 把 gunicorn 输出写入到 gunicorn.log 文件中
gunicorn --log-level debug --access-logfile gunicorn.log --worker-class=gevent -t 999 redis_chat81:app
'''

# 连接上本机的 redis 服务器
# 所以要先打开 redis 服务器
red = redis.Redis(host='127.0.0.1', port=6379, db=0)
log('redis', red)


# app = flask.Flask(__name__)
# app.secret_key = 'key'
main = Blueprint('chatroom', __name__)


# 发布聊天广播的 redis 频道
chat_channel = 'chat'


def stream():
    '''
    监听 redis 广播并 sse 到客户端
    '''
    # 对每一个用户 创建一个[发布订阅]对象
    pubsub = red.pubsub()
    # 订阅广播频道
    pubsub.subscribe(chat_channel)
    # 监听订阅的广播
    for message in pubsub.listen():
        log('steam', message)
        if message['type'] == 'message':
            data = message['data'].decode('utf-8')
            # 用 sse 返回给前端
            yield 'data: {}\n\n'.format(data)


@main.route('/subscribe')
def subscribe():
    return flask.Response(stream(), mimetype="text/event-stream")


@main.route('/')
def index_view():
    log('chatroom')
    return flask.render_template('chatroom.html')


def current_time():
    return int(time.time())


@main.route('/chat/add', methods=['POST'])
def chat_add():
    msg = request.get_json()
    name = msg.get('name', '')
    if name == '':
        name = '<匿名>'
    content = msg.get('content', '')
    channel = msg.get('channel', '')
    r = {
        'name': name,
        'content': content,
        'channel': channel,
        'created_time': current_time(),
    }
    message = json.dumps(r, ensure_ascii=False)
    # log('debug', message)
    # 用 redis 发布消息
    red.publish(chat_channel, message)
    log('red publish', chat_channel, message)
    return 'OK'

# if __name__ == '__main__':
#     config = dict(
#         debug=True,
#     )
#     app.run(**config)
