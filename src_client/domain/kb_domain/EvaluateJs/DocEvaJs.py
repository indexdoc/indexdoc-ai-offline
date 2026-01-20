# 更新文档状态
import json
import logging

import client_global


def update_doc_state(doc_id, state):
    js_code = f"""document.getElementById('本地文档AI助手').contentWindow.updateDocState('{doc_id}','{state}')"""
    try:
        client_global.client_window.evaluate_js(js_code)
    except Exception as e:
        logging.debug(e)
    return


def add_doc(item):
    param = "'" + json.dumps(item) + "'"
    js_code = f"document.getElementById('本地文档AI助手').contentWindow.loadAddDocDom({param})"
    try:
        client_global.client_window.evaluate_js(js_code)
    except Exception as e:
        logging.debug(e)
    return
