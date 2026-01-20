# 关联目录时停止，关联完目录后运行
import logging
import os
import threading
from datetime import datetime

from domain.kb_domain.serv import KBServ
import time

from domain.kb_domain.dao import KnowledgeBaseDao, DocumentDao, ViewKbDocDao
from domain.kb_domain.serv import KBServ
from domain.kb_domain.EvaluateJs import DocEvaJs


class TaskScanAndLoad:
    """
    后台任务：周期性扫描知识库变更并加载文档。
    支持四种状态：
        - RUNNING: 扫描并加载
        - SCAN_ONLY: 仅扫描变更，不加载文档
        - STOPPED: 线程结束
    """

    def __init__(self, task_duration_seconds=5):
        self._state = 'STOPPED'
        self._task_duration_seconds = task_duration_seconds
        self._thread = None
        self._loading_doc_state = 'STOPPED'

    def _start_thread(self):
        """创建并启动新线程"""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def start(self):
        """开始扫描并加载文档"""
        if self._thread is None:
            self._start_thread()
        self._state = 'RUNNING'

    def scan_only(self):
        """仅扫描变更，不加载文档"""
        self._state = 'SCAN_ONLY'

    def stop(self):
        """安全停止任务线程"""
        self._state = 'STOPPED'

    def get_state(self):
        return self._state

    def get_loading_doc_state(self):
        return self._loading_doc_state

    def _run(self):
        """线程主循环"""
        while True:
            if self._state == 'RUNNING':
                try:
                    KBServ.get_all_kb_change()
                    self.load_kb_docs() #todo 后续考虑改成并发执行，整个加载结束后再继续执行
                except Exception as e:
                    logging.debug(e)
            elif self._state == 'SCAN_ONLY':
                try:
                    KBServ.get_all_kb_change()
                except Exception as e:
                    logging.debug(e)
            time.sleep(self._task_duration_seconds)

    def load_kb_docs(self):
        # 获取待修改列表
        wait_load_list = ViewKbDocDao.get_wait_load_list()
        for _tmp in wait_load_list:
            if self._state != "RUNNING":
                break
            if _tmp['knowledge_base_id'] is not None:  # 判断是否是知识库，如为True则为知识库
                # 知识库
                if _tmp['kb_load_state'] == '已删除':
                    KnowledgeBaseDao.delete(_tmp['knowledge_base_id'])
                    # 修改前端知识库状态
                    KBServ.refresh_up_kb_state(_tmp['up_id'])
                else:
                    KBServ.refresh_up_kb_state(_tmp['knowledge_base_id'])
            else:
                # 文件
                if _tmp['kb_load_state'] == '已删除':
                    DocumentDao.delete(_tmp['document_id'])
                else:
                    doc = DocumentDao.get_by_id(_tmp['document_id'])
                    # 本地文件信息local_doc 先看是否删除
                    if not os.path.exists(doc['location_path']):
                        DocumentDao.delete(doc['document_id'])
                    # 获取本地文件大小和修改时间
                    file_stat = os.stat(doc['location_path'])
                    local_size = file_stat.st_size
                    local_timestamp = file_stat.st_mtime
                    doc['file_size'] = int(local_size)
                    doc['file_timestamp'] = int(local_timestamp)
                    from domain.kb_domain.serv.DocLoadServ import load_doc
                    self._loading_doc_state = 'RUNNING'
                    _tmp = load_doc(doc)
                    self._loading_doc_state = 'STOPPED'
                    DocumentDao.update(_tmp['document_id'], _tmp)
                # 修改前端文件状态
                DocEvaJs.update_doc_state(_tmp['document_id'], _tmp['kb_load_state'])
                # 修改待加载数量
                KBServ.update_wait_load_num()
                # 修改前端知识库状态
                KBServ.refresh_up_kb_state(_tmp['knowledge_base_id'])


# if __name__ == '__main__':
#     task = TaskScanAndLoad(task_duration_seconds=5)
#
#     # 1. 开始运行
#     task.start()
#     time.sleep(10)
#
#     # 2. 完全停止线程
#     task.stop()
#     print("Task stopped")
#
#     # 等待旧线程退出
#     import time
#
#     time.sleep(0.1)  # 确保旧线程已结束
#
#     # 3. 再次 start —— 会自动创建新线程！
#     task.start()
#     print("Task restarted")
#     time.sleep(10)
#
#     # 可以重复 stop -> start
#     task.stop()
#     time.sleep(0.1)
#     task.start()
#     print("Task restarted again")
