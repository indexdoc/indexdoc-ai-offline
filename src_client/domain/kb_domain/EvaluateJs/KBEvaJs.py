import logging

import client_global


# 更新待加载文件的数量
def update_wait_load_doc_cnt(doc_cnt):
    js_code = f"""document.getElementById('本地文档AI助手').contentWindow.changeFileNum({doc_cnt})"""
    try:
        client_global.client_window.evaluate_js(js_code)
    except Exception as e:
        logging.debug(e)
    return


def update_kb_state(kb_id, state):
    js_code = f"""document.getElementById('本地文档AI助手').contentWindow.updateKbState('{kb_id}', '{state}')"""
    try:
        client_global.client_window.evaluate_js(js_code)
    except Exception as e:
        logging.debug(e)
    return


def start_kb_loading_state():
    js_code = f"""document.getElementById('本地文档AI助手').contentWindow.startKbLoading()"""
    try:
        client_global.client_window.evaluate_js(js_code)
    except Exception as e:
        logging.debug(e)
    return


def stop_kb_loading_state():
    js_code = f"""document.getElementById('本地文档AI助手').contentWindow.stopKbLoading()"""
    try:
        client_global.client_window.evaluate_js(js_code)
    except Exception as e:
        logging.debug(e)
    return


def set_kb_loading_state_stopped():
    js_code = f"""document.getElementById('本地文档AI助手').contentWindow.setKbLoadingStopped()"""
    _loading_doc_state = client_global.task_scan_and_load.get_loading_doc_state()
    try:
        client_global.client_window.evaluate_js(js_code)
    except Exception as e:
        logging.debug(e)
    return
