from typing import Dict, Any, List, Optional
from database.sys_duckdb import exesql


# -----------------------------
# 新增知识库
# -----------------------------
def insert(data: Dict[str, Any]):
    """
    插入一条 knowledge_base 记录
    """
    fields = list(data.keys())
    placeholders = ", ".join(["?" for _ in fields])
    field_names = ", ".join(fields)

    sql = f"INSERT INTO knowledge_base ({field_names}) VALUES ({placeholders})"
    params = tuple(data.values())
    exesql(sql, params)


# -----------------------------
# 删除知识库
# -----------------------------
def delete(knowledge_base_id):
    sql = "DELETE FROM knowledge_base WHERE knowledge_base_id = ?"
    exesql(sql, (knowledge_base_id,))


# -----------------------------
# 更新知识库
# -----------------------------
def update(knowledge_base_id, data: Dict[str, Any]):
    """
    根据 knowledge_base_id 更新部分字段
    """
    if not data:
        return

    set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
    sql = f"UPDATE knowledge_base SET {set_clause} WHERE knowledge_base_id = ?"
    params = tuple(data.values()) + (knowledge_base_id,)
    exesql(sql, params)


# -----------------------------
# 查询单条
# -----------------------------
def get_by_id(knowledge_base_id) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM knowledge_base WHERE knowledge_base_id = ?"
    rows = exesql(sql, (knowledge_base_id,))
    return rows[0] if rows else None


# -----------------------------
# 查询全部（可带过滤条件）
# -----------------------------
def get_all(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    sql = "SELECT * FROM knowledge_base"
    params = ()

    if filters:
        conds = [f"{k} = ?" for k in filters.keys()]
        sql += " WHERE " + " AND ".join(conds)
        params = tuple(filters.values())

    rows = exesql(sql, params)
    return rows


# -----------------------------
# 查询知识库目录（可带过滤条件）
# -----------------------------
def get_dir_list(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    sql = f"""
        SELECT 
            knowledge_base_id,
            location_path
        FROM knowledge_base
        """
    params = ()

    if filters:
        conds = [f"{k} = ?" for k in filters.keys()]
        sql += " WHERE " + " AND ".join(conds)
        params = tuple(filters.values())

    rows = exesql(sql, params)
    return rows

# -----------------------------
# 查询待加载的知识库及文件（可带过滤条件）
# -----------------------------
def get_wait_load_kb(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    sql = f"""
        SELECT 
            knowledge_base_id,
            location_path
        FROM knowledge_base
        """
    params = ()

    if filters:
        conds = [f"{k} = ?" for k in filters.keys()]
        sql += " WHERE " + " AND ".join(conds)
        params = tuple(filters.values())

    rows = exesql(sql, params)
    return rows
