# 对指定知识库向量检索
import os
from typing import Dict, Tuple, List

import client_global
from domain.kb_domain.EvaluateJs.DocEvaJs import add_doc
from domain.kb_domain.EvaluateJs.KBEvaJs import stop_kb_loading_state, start_kb_loading_state, update_kb_state
from util import IDUtil
from domain.kb_domain.dao import KnowledgeBaseDao, DocumentDao, ViewKbDocDao
from domain.kb_domain.serv import DirServ


# kb_change_type: "新增、删除 "ADDED,DELETED
# doc_change_type: "新增、删除、修改" "ADDED,DELETED,MODIFIED"
# 获取知识库对应的文件目录的更新情况
def get_kb_change(kb_id) -> ([dict], [dict]):
    # 待task处理内容
    kb_list = []
    kb_doc_list = []

    # 获取当前信息
    kb = KnowledgeBaseDao.get_by_id(kb_id)
    dir_list, fileinfo_list, exists = DirServ.get_dir_content(kb['location_path'])

    if not exists:
        KnowledgeBaseDao.update(kb_id, {'kb_load_state': "已删除"})
        update_kb_state(kb_id, '已删除')

    # 获取知识库文件信息
    kb_fileinfo_list = DocumentDao.get_fileinfo_list({'knowledge_base_id': kb_id})
    # 获取知识库信息
    kb_dir_list = KnowledgeBaseDao.get_dir_list({'up_id': kb_id})

    # 与知识库进行比对
    added_dirs, deleted_dirs, modified_dirs = compare_list(kb_dir_list, dir_list)

    added_files, deleted_files, modified_files = compare_list(kb_fileinfo_list, fileinfo_list)

    for _dir in added_dirs:
        _id = IDUtil.get_long()
        KnowledgeBaseDao.insert(
            {'knowledge_base_id': _id, 'up_id': kb_id,
             'knowledge_base_name': get_last_folder_name(_dir["location_path"]),
             'location_path': _dir["location_path"],
             'kb_load_state': "新增,待加载"})
        kb_list.append({'knowledge_base_id': _id, 'action': 'add'})

    for _dir in deleted_dirs:
        KnowledgeBaseDao.update(_dir['knowledge_base_id'], {'kb_load_state': "已删除"})
        kb_list.append({'knowledge_base_id': _dir['knowledge_base_id'], 'action': 'delete'})

    # 写数据库的document和kb，更新“加载状态”
    for file in added_files:
        _id = IDUtil.get_long()
        DocumentDao.insert({
            "document_id": _id,
            "knowledge_base_id": kb_id,
            "file_name": file['file_short_name'],
            "metadata": file['metadata'],
            "file_type": file['file_short_name'].split('.')[-1] if '.' in file['file_short_name'] else '',
            "file_size": file['file_size'],
            "location_path": file['location_path'],
            "file_timestamp": file['file_timestamp'],
            "kb_load_state": "新增,待加载"
        })
        kb_doc_list.append({'document_id': _id, 'action': 'add'})

    for file in deleted_files:
        DocumentDao.update(file['document_id'], {'kb_load_state': '已删除'})
        kb_doc_list.append({'document_id': file['document_id'], 'action': 'delete'})

    for _document_id, file in modified_files:
        DocumentDao.update(_document_id, {'kb_load_state': '已修改,待加载', 'file_size': file['file_size'], 'file_timestamp': file['file_timestamp']})
        kb_doc_list.append({'document_id': _document_id, 'action': 'modified'})

    # 更新前端待加载文件数量
    update_wait_load_num()
    for item in kb_list:
        if item['action'] == 'add':
            _item = ViewKbDocDao.get_all({'knowledge_base_id': item['knowledge_base_id']})
            add_doc(_item[0])
    for item in kb_doc_list:
        if item['action'] == 'add':
            _item = ViewKbDocDao.get_all({'document_id': item['document_id']})
            add_doc(_item[0])
    child_dir = KnowledgeBaseDao.get_all({'up_id': kb_id})
    for child in child_dir:
        get_kb_change(child['knowledge_base_id'])
    return kb_list, kb_doc_list


# 取出目录最后一个文件夹的名称
def get_last_folder_name(path):
    # 处理路径分隔符的兼容性
    path = os.path.normpath(path)
    # 获取最后一个文件夹名称
    return os.path.basename(path)


def get_all_kb_change():
    kb_list = KnowledgeBaseDao.get_all({'up_id': '0'})
    for kb in kb_list:
        get_kb_change(kb['knowledge_base_id'])


def compare_list(
        kb_list: List[Dict],
        fs_list: List[Dict]
) -> Tuple[List[Dict], List[Dict], List[Tuple[str, Dict]]]:
    """
    对比数据库和文件系统文件列表（只比较 file_size 和 file_timestamp）
    返回：
      - 新增列表（fs_dict）
      - 删除列表（kb_dict）
      - 修改列表 [(document_id, fs_dict)]
    """
    # 构建索引：使用 location_path 作为唯一键
    kb_map = {f["location_path"]: f for f in kb_list}
    fs_map = {f["location_path"]: f for f in fs_list}

    kb_keys = set(kb_map.keys())
    fs_keys = set(fs_map.keys())

    # 新增：文件系统有，数据库没有
    added_files = [fs_map[k] for k in fs_keys - kb_keys]

    # 删除：数据库有，文件系统没有
    deleted_files = [kb_map[k] for k in kb_keys - fs_keys]

    # 修改：两边都有，但 file_size 或 file_timestamp 不同
    modified_files = []
    for k in kb_keys & fs_keys:
        kb_f = kb_map[k]
        fs_f = fs_map[k]
        if kb_f.get('file_size') is not None:
            if (kb_f["file_size"] != fs_f["file_size"]) or (abs(kb_f["file_timestamp"] != fs_f["file_timestamp"])):
                modified_files.append((kb_f["document_id"], fs_f))


    return added_files, deleted_files, modified_files


# 更新前端待加载文件数量
def update_wait_load_num(num=None):
    if num is None:
        num = DocumentDao.get_wait_load_num()
    from domain.kb_domain.EvaluateJs import KBEvaJs
    KBEvaJs.update_wait_load_doc_cnt(int(num['num']))


# 根据知识库id递归移除下面所有的知识库和文档
def kb_delete_all(kb_id):
    doc_delete_list = DocumentDao.get_all({'knowledge_base_id': kb_id})
    for doc in doc_delete_list:
        DocumentDao.delete(doc['document_id'])
    kb_delete_list = KnowledgeBaseDao.get_all({'up_id': kb_id})
    for kb in kb_delete_list:
        kb_delete_all(kb['knowledge_base_id'])
    KnowledgeBaseDao.delete(kb_id)



def refresh_up_kb_state(up_id):
    wait_load_list = ViewKbDocDao.get_wait_load_list(up_id)
    if len(wait_load_list) == 0:
        kb_load_state = '完成'
        KnowledgeBaseDao.update(up_id, {'kb_load_state': kb_load_state})
        from domain.kb_domain.EvaluateJs.KBEvaJs import update_kb_state
        update_kb_state(up_id, kb_load_state)
        kb = KnowledgeBaseDao.get_by_id(up_id)
        if kb['up_id'] == '0':
            return
        refresh_up_kb_state(kb['up_id'])

    # kbs = KnowledgeBaseDao.get_all()
    # for kb in kbs:
    #     kb_list, kb_doc_list = get_kb_change(kb['knowledge_base_id'])
    #     for action_kb in kb_list:
    #         if action_kb['action'] == 'delete':
    #             KnowledgeBaseDao.delete(action_kb['knowledge_base_id'])
    #     for action_doc in kb_doc_list:
    #         from domain.kb_domain.serv.DocLoadServ import load_doc
    #         if action_doc['action'] == 'delete':
    #             DocumentDao.delete(action_doc['document_id'])
    #         elif action_doc['action'] == 'add':
    #             document = DocumentDao.get_by_id(action_doc['document_id'])
    #             document = load_doc(document)
    #             DocumentDao.update(document['document_id'], document)
    #         elif action_doc['action'] == 'modified':
    #             document = DocumentDao.get_by_id(action_doc['document_id'])
    #             document = load_doc(document)
    #             DocumentDao.update(document['document_id'], document)
    #         update_wait_load_num()
    # 修改前端知识库状态


def delete_kb_byid(kb_id):
    KnowledgeBaseDao.delete(kb_id)
