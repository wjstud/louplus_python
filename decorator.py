# -*- coding: utf-8 -*-
from functools import wraps
from datetime import datetime

#  装饰器的经典运用
def log(func):
    @wraps(func) # 解决装饰器副作用, 装饰后的函数变成了 decorator 函数
    def decorator(*args, **kwargs):
        print('Function ' + func.__name__ + ' has been called at ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return func(*args, **kwargs)
    return decorator

@log
def add(x, y):
    return x + y

if __name__ == '__main__':
    add(1, 2)
    print(add.__name__)
