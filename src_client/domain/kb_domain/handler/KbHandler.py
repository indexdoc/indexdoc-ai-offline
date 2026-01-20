import json
import logging
import subprocess
import sys
import os
import threading
import time

import webview

import client_global
from domain.base_domain.BaseHandler import BaseApiHandler
from domain.kb_domain.dao import KnowledgeBaseDao
from domain.kb_domain.dao import DocumentDao
from domain.kb_domain.dao import ViewKbDocDao

from domain.kb_domain.serv.KBServ import get_kb_change, kb_delete_all, update_wait_load_num
from util import IDUtil

sleep_time = 0.2


class ApiAddKbHandler(BaseApiHandler):
    need_login = False

    def myget(self):
        # 创建一个隐藏的主窗口（不显示）
        result = webview.windows[0].create_file_dialog(webview.FileDialog.FOLDER)
        # 如果用户点击“取消”，selected_dir 会是空字符串
        if result:
            # 后台任务
            while client_global.task_scan_and_load is None:
                time.sleep(sleep_time)
            client_global.task_scan_and_load.stop()
            dir_path = result[0]
            kbs = KnowledgeBaseDao.get_all({'knowledge_base_name': dir_path})
            if len(kbs) == 0:
                _id = IDUtil.get_long()
                # 创建最外层目录知识库
                KnowledgeBaseDao.insert(
                    {'knowledge_base_id': _id, 'up_id': '0', 'knowledge_base_name': result[0],
                     'location_path': result[0], 'kb_load_state': "新增,待加载"})
                get_kb_change(_id)
                # 后台任务
                client_global.task_scan_and_load.start()
                self.write({"status": "success", "data": {'id': _id, 'dir': result[0]}, 'msg': '文件加载完成'})
            else:
                self.write({"status": "fail", "data": "不能重复关联。"})
        else:
            self.write({"status": "fail", "data": "未选择任何目录。"})


class ApiRemoveDocHandler(BaseApiHandler):
    need_login = False

    def myget(self):
        document_id = self.get_argument("document_id", None)
        if document_id is None:
            self.write({
                'status': False,
                'msg': '请选中文件',
            })
        document = DocumentDao.get_by_id(document_id)
        if not document:
            self.write({
                'status': False,
                'msg': '未找到文件',
            })
        DocumentDao.delete(document_id)
        self.write({
            'status': True,
            'msg': '成功',
        })


class ApiViewKbDocListHandler(BaseApiHandler):
    need_login = False

    def myget(self):
        _limit = self.get_arg('limit')
        _page = self.get_arg('page')
        _search_params = self.get_arg('searchParams')  # JSON格式传数据
        _limit = 50000 if _limit is None else int(_limit)
        _page = 1 if _page is None else int(_page)
        if _search_params is not None:
            _search_params = json.loads(_search_params)

        _dict_list, _cnt = ViewKbDocDao.get_all_page(int(_limit), (int(_page) - 1) * int(_limit),
                                                     _search_params)
        self.write({
            'success': True,
            'code': 0,
            'msg': None,
            'count': _cnt,
            'data': _dict_list
        })


class ApiViewKbIdListHandler(BaseApiHandler):
    need_login = False

    def myget(self):
        _search_params = self.get_arg('searchParams')  # JSON格式传数据
        if _search_params is not None:
            _search_params = json.loads(_search_params)

        id_list = ViewKbDocDao.get_id_list(_search_params['name'])
        self.write({
            'success': True,
            'code': 0,
            'msg': None,
            'data': json.dumps(id_list)
        })


class ApiWaitDocNumHandler(BaseApiHandler):
    need_login = False

    def myget(self):
        num = DocumentDao.get_wait_load_num()
        self.write({
            'success': True,
            'code': 0,
            'msg': None,
            'data': num
        })


# 打开目录的api
class ApiOpenDirHandler(BaseApiHandler):
    need_login = False

    def myget(self):
        # 前端通过 searchParams 传递 JSON
        search_params = self.get_argument("searchParams", None)

        try:
            params = json.loads(search_params)
            dir_path = params.get("dir_path", None)
        except Exception:
            self.write({
                "success": False,
                "msg": f"打开目录失败"
            })
            return

        # 校验路径是否存在
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            self.write({
                "success": False,
                "msg": f"路径不存在或不是目录: {dir_path}"
            })
            return

        try:
            os.startfile(dir_path)
            self.write({
                "success": True,
                "msg": f"目录已打开: {dir_path}"
            })
        except Exception as e:
            self.write({
                "success": False,
                "msg": f"打开目录失败"
            })


# 打开文件的qpi
class ApiOpenFileHandler(BaseApiHandler):
    need_login = False

    def myget(self):
        search_params = self.get_argument("searchParams", None)
        try:
            params = json.loads(search_params)
            path = params.get("file_path", None)
            if not os.path.exists(path):
                self.write({
                    "success": False,
                    "msg": "文件不存在"
                })
                return
        except Exception:
            self.write({
                "success": False,
                "msg": "文件打开失败"
            })
            return

        try:
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.call(['open', path])
            else:  # Linux
                subprocess.call(['xdg-open', path])
            self.write({
                "success": True,
                "msg": "打开成功"
            })
            return
        except Exception as e:
            logging.debug(e)


class ApiStartKbLoadingHandler(BaseApiHandler):
    need_login = False

    def get(self):
        while client_global.task_scan_and_load is None:
            time.sleep(sleep_time)
        client_global.task_scan_and_load.start()
        self.write({'success': True, 'msg': ''})


class ApiStopKbLoadingHandler(BaseApiHandler):
    need_login = False

    async def get(self):
        try:
            while client_global.task_scan_and_load is None:
                time.sleep(sleep_time)
            client_global.task_scan_and_load.scan_only()
            self.write({'success': True, 'msg': '', 'data': 'stopping'})
            self.finish()

            # 后台线程执行 stop 逻辑
            threading.Thread(target=self._stop_task_background, daemon=True).start()
        except Exception as e:
            msg = f"停止知识库文件加载失败： {e}"
            logging.error(f'{e.__class__.__name__}: {msg}')
            self.write({
                "success": False,
                "msg": "停止知识库文件加载失败"
            })
            return

    def _stop_task_background(self):
        """后台执行停止任务"""
        try:
            client_global.task_scan_and_load.scan_only()
            # 等待停止
            while client_global.task_scan_and_load.get_loading_doc_state() == "RUNNING":
                time.sleep(0.5)
            from domain.kb_domain.EvaluateJs import KBEvaJs
            KBEvaJs.set_kb_loading_state_stopped()
        except Exception as e:
            logging.error(f"后台停止知识库加载失败：{e}")

class ApiRemoveKBHandler(BaseApiHandler):
    need_login = False

    def myget(self):
        knowledge_base_id = self.get_argument("kb_id", None)
        # 后台任务
        while client_global.task_scan_and_load is None:
            time.sleep(sleep_time)
        client_global.task_scan_and_load.scan_only()
        try:
            # 删除顶级
            kb_delete_all(knowledge_base_id)
            self.write({
                "success": True,
                "msg": "删除成功"
            })
            update_wait_load_num()
            # 后台任务
            client_global.task_scan_and_load.start()
            return
        except Exception as e:
            msg = f"删除知识库时出现意外： {e}"
            logging.error(f'{e.__class__.__name__}: {msg}')
            self.write({
                "success": False,
                "msg": "删除知识库时出现意外"
            })
            return


urls = [
    ('/api/knowledge/addKb', ApiAddKbHandler),
    # ('/api/knowledge/removeDoc', ApiRemoveDocHandler),
    ('/api/knowledge/ViewKbDoc/list', ApiViewKbDocListHandler),
    ('/api/knowledge/ViewKbDoc/kbIdList', ApiViewKbIdListHandler),
    ('/api/knowledge/openDir', ApiOpenDirHandler),
    ('/api/knowledge/openFile', ApiOpenFileHandler),
    ('/api/knowledge/getWaitDocNum', ApiWaitDocNumHandler),
    ('/api/knowledge/startKbLoading', ApiStartKbLoadingHandler),
    ('/api/knowledge/stopKbLoading', ApiStopKbLoadingHandler),
    ('/api/knowledge/removeKB', ApiRemoveKBHandler)
]
