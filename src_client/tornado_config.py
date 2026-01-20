import os
import sys

import frozen_support
base_path = frozen_support.get_base_path()
html_path = os.path.join(base_path, 'html')
favicon_file = os.path.join(base_path, 'html/favicon-indexdoc.ico')
static_path = os.path.join(base_path, 'html/pc/static')  # 无需登陆也可以访问的资源
page_path = os.path.join(base_path, 'html/pc/page')  # 业务处理的页面，需要校验每个页面的用户权限
html_pc_path = os.path.join(base_path, 'html/pc')  # 业务处理的页面，需要校验每个页面的用户权限
public_path = os.path.join(base_path, 'html/pc/public')  # 需要用户登陆才能访问，但是不需要配置用户权限
template_path = os.path.join(base_path, 'template')
tmp_path = os.path.join(base_path, 'tmp')
log_path = os.path.join(base_path, 'log')
if not os.path.exists(tmp_path):
    os.makedirs(tmp_path)
if not os.path.exists(log_path):
    os.makedirs(log_path)

error_page_file = os.path.join(base_path, 'html/pc/404.html')
error_url = '/pc/404'
default_index_file = os.path.join(base_path, 'html/pc/index.html')

port = 50001


