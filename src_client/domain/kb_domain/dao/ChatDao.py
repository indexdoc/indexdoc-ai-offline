from typing import Dict, Any, List, Optional
from database.sys_duckdb import exesql


# -----------------------------
# 新增会话
# -----------------------------
def insert(data: Dict[str, Any]):
    """
    插入一条 chat 记录
    """
    fields = list(data.keys())
    placeholders = ", ".join(["?" for _ in fields])
    field_names = ", ".join(fields)

    sql = f"INSERT INTO chat ({field_names}) VALUES ({placeholders})"
    params = tuple(data.values())
    exesql(sql, params)


# -----------------------------
# 删除会话
# -----------------------------
def delete(chat_id: str):
    sql = "DELETE FROM chat WHERE chat_id = ?"
    exesql(sql, (chat_id,))


# -----------------------------
# 更新会话
# -----------------------------
def update(chat_id: str, data: Dict[str, Any]):
    """
    根据 chat_id 更新部分字段
    """
    if not data:
        return

    set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
    sql = f"UPDATE chat SET {set_clause} WHERE chat_id = ?"
    params = tuple(data.values()) + (chat_id,)
    exesql(sql, params)


# -----------------------------
# 查询单条
# -----------------------------
def get_by_id(chat_id: str) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM chat WHERE chat_id = ?"
    rows = exesql(sql, (chat_id,))
    return rows[0] if rows else None


# -----------------------------
# 查询全部（可带过滤条件）
# -----------------------------
def get_all(filters: Optional[Dict[str, Any]] = None):
    sql = "SELECT * FROM chat"
    params = ()

    if filters:
        conds = [f"{k} = ?" for k in filters.keys()]
        sql += " WHERE " + " AND ".join(conds)
        params = tuple(filters.values())
    sql += " order by chat_id desc"

    rows = exesql(sql, params)
    return rows
