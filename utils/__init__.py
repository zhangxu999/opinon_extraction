"""
这里放置一些工具函数，和工具类。
"""
import time
import threading
from flask import g
thread_local = threading.local()
thread_local.need = True
def create_a_log():
    if not False:
        return
    now = str(time.time())
    name = 'static/log/{}.log'.format(now)
    thread_local.logger = open(name,'a')
    return thread_local
    
def write_a_log(stage,sub_title,value):
    if not False:
        return
    if not hasattr(thread_local,'logger'):
        create_a_log()
    content = '---{}:::{}    {}\n'.format(stage,sub_title,str(value))
    thread_local.logger.write(content)

def close_a_log():
    if not False:
        return
    thread_local.logger.close()