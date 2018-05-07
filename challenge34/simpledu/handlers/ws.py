from flask import Blueprint
import redis, gevent, json

ws = Blueprint('ws', __name__, url_prefix='/ws')

redis = redis.from_url('redis://127.0.0.1:6379')

class Chatroom(object):
    """ 主要用于管理客户端连接，以及向所有客户端发送消息，
        然后用 gevent 异步启动聊天室，
        接着使用 flask-sockets 提供的方式实现了俩个接口: 
               一个用于从客户端接收消息（inbox）
               一个负责注册请求消息的客户端到聊天室 """

    def __init__(self):
        self.clients = []
        # 初始化 pubsub 系统
        self.pubsub = redis.pubsub()
        # 订阅chat 频道
        self.pubsub.subscribe('chat')

    def register(self, client):
        self.clients.append(client)

    def send(self, client, data):
        # 给每一个客户端 client 发送消息 data
        try:
            # Python3 中接收到的消息是二进制的, 使用 decode 函数转化为字符串
            client.send(data.decode('utf-8'))

        except:
            # 发生错误可能是客户端已经关闭, 移除该客户端
            self.clients.remove(client)

    def run(self):
        # 依次将接收到的消息再发送给所有客户端
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = message.get('data')
                for client in self.clients:
                    # 使用 gevent 异步发送
                    gevent.spawn(self.send, client, data)

    def start(self):
        # 异步执行 run 函数
        gevent.spawn(self.run)

# 初始化聊天室
chat = Chatroom()
# 异步启动聊天室
chat.start()

@ws.route('/send')
def index(ws):
    # 使用 flask-sockets，ws 链接对象会被自动注入到路由处理函数
    # 该处理函数用来处理前端连接发过来的消息。注意下面的 while 循环，
    # 里面 receive() 函数实际是在阻塞运行的，直到前端发送消息过来
    # 消息会被放入到 chat 频道，也就是我们的消息队列中，这样一直循环
    # 直到 websocket 连接关闭
    while not ws.closed:
        gevent.sleep(0.1)
        message = ws.receive()
        if message:
            # 发送消息到 chat 频道
            redis.publish('chat', message)

@ws.route('/recv')
def outbox(ws):
    # 该函数用来注册客户端连接，并在 Chatroom 中将从其他客户端接收
    # 到的消息发送给这些客户端
    chat.register(ws)
    # 以后需实现 ”欢迎某某进入直播间“ 
    redis.publish('chat', json.dumps(dict(
        username='New user come in, people count',
        text=len(chat.clients)
        )))
    while not ws.closed:
        gevent.sleep(0.1)
