import background_init
import json
import time
import multiprocessing

import client_global
import signal
import socket

import webview
import logging
import psutil
import frozen_support

import os
import glob
# comm_file = frozen_support.get_resource_path(f'../tmp/.launch_status_{os.getpid()}.json')

tmp_path = frozen_support.get_tmp_path()
comm_file = tmp_path + f'/.launch_status_{os.getpid()}.json'


def find_free_port():
    with socket.socket() as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def delete_tmp_files(file_path=tmp_path, file_pattern='.launch_status_*.json'):
    file_path = frozen_support.get_resource_path(file_path)
    _files = glob.glob(os.path.join(file_path, file_pattern))
    for _file in _files:
        try:
            os.remove(_file)
        except Exception as e:
            logging.debug(e)


def on_close():
    pid = os.getpid()  # 当前 Python 进程 PID
    p = psutil.Process(pid)
    try:
        os.remove(comm_file)
        delete_tmp_files(file_pattern='.launch_status_*.json')
        delete_tmp_files(file_pattern='*.docx')
        import shutil
        shutil.rmtree(frozen_support.get_tmp_path()+r'\update_work', ignore_errors=True)
    except:
        pass
    p.send_signal(signal.SIGTERM)  # 等同于停止按钮发送的终止信号

def on_window_closing():
    """
    当窗口即将关闭时调用。
    返回 True 表示允许关闭，返回 False 表示取消关闭。
    """
    # 使用 pywebview 内置的确认对话框（完全在 Python 中）
    result = client_global.client_window.create_confirmation_dialog(
        title='⚠️ 确认退出 IndexDoc',  # 添加警告 emoji
        message='❌ 您确定要退出吗？'
    )

    if result:
        # print("用户确认退出，关闭应用。")
        return True  # 允许关闭
    else:
        # print("用户取消退出。")
        return False  # 阻止关闭


def send_status_to_parent_process(status="启动中", progress=0):
    try:
        # 如果没有传入 comm_file，则使用默认命名规则
        global comm_file
        # 主程序自身的路径
        import sys
        signal_data = {
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S"),
            "pid": os.getpid(),
            "process_name": "_indexdoc_win.bin",
            "status": status,
            "progress": progress
        }

        with open(comm_file, 'w', encoding='utf-8') as f:
            json.dump(signal_data, f, ensure_ascii=False)
        logging.debug(f"已向主进程发送状态信号: status={status}, progress={progress}")
    except Exception as e:
        logging.debug(f"发送状态信号失败: {e}")


def main():
    send_status_to_parent_process(status="开始启动", progress=0)
    multiprocessing.freeze_support()
    if frozen_support.is_frozen(): #解决使用windows直接解压zip文件时，windows会锁定解压生成的dll的问题
        if frozen_support.is_file_blocked(r".\_internal\pythonnet\runtime\Python.Runtime.dll"):
            frozen_support.unblock_files()
            logging.info("发现windows锁定了dll文件，已全部解锁。")
    background_init.load_embedding_model()  # 预加载向量模型以提速，此函数会自动启动一个线程执行任务
    send_status_to_parent_process(status="启动中", progress=10)
    import js_api
    import tornado_server
    send_status_to_parent_process(status="启动中", progress=50)
    if frozen_support.is_frozen():
        port = find_free_port()
    else:
        port = 8080
    client_global.web_port = port
    import threading
    # 在新线程中运行 Tornado 服务器
    server_thread = threading.Thread(target=tornado_server.start_tornado, args=(port, 0), daemon=True)
    server_thread.start()
    webview.settings['ALLOW_DOWNLOADS'] = True
    send_status_to_parent_process(status="启动中", progress=90)
    client_global.client_window = webview.create_window(
        'IndexDoc：个人 AI 工作台，专业文档服务平台——简单，智能，高效',
        url=f'http://localhost:{port}',
        width=1600,
        height=900,
        js_api=js_api.JSApi(None),
        min_size=(1200, 800)
        # confirm_close=True,
        # localization={'global.quitConfirmation': '确定要退出吗?',
        #               },
    )

    # 注入自定义脚本
    def inject_scripts():
        send_status_to_parent_process(status="启动完成", progress=100)
        client_global.client_window.load_css("body { background-color: #f0f0f0; }")
        background_init.warm_up_wx_api()  # 预热api的访问以提速，此函数会自动启动一个线程执行

    # 绑定加载完成事件
    client_global.client_window.events.closing += on_window_closing
    client_global.client_window.events.loaded += inject_scripts
    client_global.client_window.events.closed += on_close
    if frozen_support.is_frozen():
        webview.start(debug=False)
    else:
        webview.start(debug=True)


if __name__ == "__main__":
    main()
