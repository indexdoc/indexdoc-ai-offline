import json
from typing import List, Dict, Any, Optional

from database.sys_duckdb import exesql


# -----------------------------
# 查询全部（可加条件）
# -----------------------------
def get_all(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    sql = "SELECT * FROM view_kb_doc"
    params = ()

    if filters:
        conds = []
        for k, v in filters.items():
            conds.append(f"{k} = ?")
        sql += " WHERE " + " AND ".join(conds)
        # sql += " order by name"
        params = tuple(filters.values())

    rows = exesql(sql, params)
    return rows


# -----------------------------
# 查询全部（可加条件）
# -----------------------------
def get_all_page(cnt=5000, start=0, filters: Optional[Dict[str, Any]] = None):
    sql = "SELECT * FROM view_kb_doc "
    params = ()
    if filters:
        conds = []
        for k, v in filters.items():
            if k == "kb_doc_id_list":
                v = json.loads(v)
                if isinstance(v, list) and len(v) > 0:
                    id_list = [str(i) for i in v if i is not None]
                    id_in = ",".join(f"'{i}'" for i in id_list)
                    conds.append(
                        f"(knowledge_base_id IN ({id_in}) OR document_id IN ({id_in}))"
                    )
            else:
                conds.append(f"{k} = '{v}'")
        sql += " WHERE " + " AND ".join(conds)
        # sql += " order by name"
    # sql += f' limit {cnt} '
    rows = exesql(sql)
    return rows, len(rows)


# -----------------------------
# 查询知识库ID、文件ID
# -----------------------------
def get_id_list(name):
    sql = f"SELECT document_id, knowledge_base_id, up_id FROM view_kb_doc WHERE name LIKE '%{name}%'"
    rows = exesql(sql)

    if not rows:
        return []

    all_ids = set()

    def get_parents(doc_or_kb_id, is_kb):
        """递归查上级"""
        if is_kb:
            sql_parent = f"SELECT up_id FROM view_kb_doc WHERE knowledge_base_id = '{doc_or_kb_id}'"
        else:
            sql_parent = f"SELECT up_id FROM view_kb_doc WHERE document_id = '{doc_or_kb_id}'"

        parent = exesql(sql_parent)
        if parent and parent[0]['up_id']:
            pid = parent[0]['up_id']
            if pid not in all_ids:
                all_ids.add(pid)
                # 递归查上级（假设上级一定是知识库）
                get_parents(pid, is_kb=True)

    for row in rows:
        if row.get('knowledge_base_id'):
            all_ids.add(row['knowledge_base_id'])
            get_parents(row['knowledge_base_id'], is_kb=True)
        else:
            all_ids.add(str(row['document_id']))
            get_parents(row['document_id'], is_kb=False)

    return list(all_ids)


# -----------------------------
# 查询获取待加载文件（可加条件）
# -----------------------------
def get_wait_load_list(kb_id=None) -> List[Dict[str, str]]:
    where = ' where '
    if kb_id:
        where += f" up_id = '{kb_id}' and "
    sql = f"SELECT * FROM view_kb_doc {where} (kb_load_state like '%待加载%' or kb_load_state = '已删除') "
    rows = exesql(sql)
    return rows


# -----------------------------
# 查询获取待加载文件（可加条件）
# -----------------------------
def get_add_list(kb_id=None) -> List[Dict[str, str]]:
    where = ' where '
    if kb_id:
        where += f" up_id = '{kb_id}' and "
    sql = f"SELECT * FROM view_kb_doc {where} (kb_load_state like '%新增%' ) "
    rows = exesql(sql)
    return rows

