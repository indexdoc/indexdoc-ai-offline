import os
from domain import SysHandler
from domain import domain_urls
from util.JsonUtil import EkyJsonEncoder
import tornado_config
import logging
import json
import functools
import tornado

# 设置json可以处理datetime格式
json.dumps = functools.partial(json.dumps, cls=EkyJsonEncoder)
# 对html的目录进行监听并自动重启
# tornado.autoreload.watch(tornado_config.html_path)
# for dirpath, dirnames, filenames in os.walk(tornado_config.html_path):
#     for dirname in dirnames:
#         full_path = os.path.join(dirpath, dirname)
#         tornado.autoreload.watch(full_path)
#     for filename in filenames:
#         full_path = os.path.join(dirpath, filename)
#         tornado.autoreload.watch(full_path)

# 获取各个模块的url路由
urls = [
    (r'/pc/static/(.*)', tornado.web.StaticFileHandler, {'path': tornado_config.static_path}),
    ('/', SysHandler.DefaultIndexHandler),
]
urls += SysHandler.urls
urls += domain_urls.urls
settings = {
    'handlers': urls,
    'debug': True,
    'autoreload': False,
    'cookie_secret': '089883748324238429492348ssaasdfsdc',
    'default_handler_class': SysHandler.MyErrortHandler,

}
app = tornado.web.Application(**settings)
def start_tornado(port, a):
    """ 启动 Tornado 服务器 """
    try:
        app.listen(port)
        logging.info(f"Tornado Web Server Start at Port {port}")
        # 预加载权限缓存
        # logging.info("加载权限缓存 begin")
        # # SysCache.refreshAuth()
        # logging.info("加载权限缓存 end")
        # 启动 Tornado 事件循环
        # tornado.autoreload.start()
        tornado.ioloop.IOLoop.current().start()
    except Exception as e:
        logging.error(f"服务器启动失败: {e}")
