from typing import List, Dict, Any, Optional

import numpy as np

from database.sys_duckdb import exesql


# -----------------------------
# 新增文档
# -----------------------------
def insert(data: Dict[str, Any]):
    """
    插入一条 document 记录
    :param data: 字段名 -> 值 的字典
    """
    fields = list(data.keys())
    placeholders = ", ".join(["?" for _ in fields])
    field_names = ", ".join(fields)

    sql = f"INSERT INTO document ({field_names}) VALUES ({placeholders})"
    params = tuple(data.values())
    exesql(sql, params)


# -----------------------------
# 新增文档-批量操作
# -----------------------------
def insert_many(data_list: List[Dict[str, Any]]):
    """
    批量插入 document 记录
    :param data_list: 每个元素是一个 dict，表示一条记录
    """
    if not data_list:
        return

    fields = list(data_list[0].keys())
    placeholders = ", ".join(["?" for _ in fields])
    field_names = ", ".join(fields)

    sql = f"INSERT INTO document ({field_names}) VALUES ({placeholders})"

    params = []
    for item in data_list:
        # 按 fields 顺序提取每个字段的值
        row = tuple(item[field] for field in fields)
        # 添加到批量参数列表
        params.append(row)

    # 执行批量插入
    exesql(sql, params, is_many_insert=True)


# -----------------------------
# 删除文档
# -----------------------------
def delete(document_id):
    sql = "DELETE FROM document WHERE document_id = ?"
    exesql(sql, (document_id,))


# -----------------------------
# 更新文档
# -----------------------------
def update(document_id, data: Dict[str, Any]):
    """
    根据 document_id 更新部分字段
    """
    if not data:
        return

    set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
    sql = f"UPDATE document SET {set_clause} WHERE document_id = ?"
    params = tuple(data.values()) + (document_id,)
    exesql(sql, params)


# -----------------------------
# 查询单条
# -----------------------------
def get_by_id(document_id) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM document WHERE document_id = ?"
    rows = exesql(sql, (document_id,))
    if not rows:
        return None
    return dict(rows[0])


# -----------------------------
# 查询全部（可加条件）
# -----------------------------
def get_all(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    sql = "SELECT * FROM document"
    params = ()

    if filters:
        conds = []
        for k, v in filters.items():
            conds.append(f"{k} = ?")
        sql += " WHERE " + " AND ".join(conds)
        params = tuple(filters.values())

    rows = exesql(sql, params)
    return [dict(row) for row in rows]


# -----------------------------
# 查询获取待加载文件数量（可加条件）
# -----------------------------
def get_wait_load_num(kb_id=None) -> Dict[str, str]:
    where = ' where '
    if kb_id:
        where += f" knowlegde_base_id = '{kb_id}' "
    sql = f"SELECT count(*) as num FROM document {where} (kb_load_state like '%待加载%' or kb_load_state = '已删除') "
    rows = exesql(sql)
    return rows[0]


# -----------------------------
# 查询文件基础信息（可加条件）
# -----------------------------
def get_fileinfo_list(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    sql = """
        SELECT 
            document_id,
            file_name AS file_short_name,
            file_type,
            metadata AS meta_data,
            location_path,
            file_size,
            file_timestamp
        FROM document
    """
    params = ()

    if filters:
        conds = []
        for k, v in filters.items():
            if v is not None and v != '':
                conds.append(f"{k} = ?")
        sql += " WHERE " + " AND ".join(conds)
        params = tuple(filters.values())

    rows = exesql(sql, params)
    return [dict(row) for row in rows]


# -----------------------------
# 根据查询分片的下标取出对应的文本内容
# -----------------------------
def get_doc_by_chunk_index(document_id, chunk_index_list) -> Dict[str, Any]:
    sql = f"""
        SELECT 
            document_id,
            document_uuid,
            knowledge_base_id,
            file_name,
            knowledge_name,
            file_type,
            metadata,
            location_path,
            file_summary,
            array_to_string(
                list_transform(
                    {chunk_index_list},
                    idx -> file_content_chunks[idx + 1]
                ),
                ''
            ) AS file_content,
            file_name_vector,
            file_size,
            file_timestamp,
            kb_load_state,
            markdown,
            extend_attrs,
            order_no,
            create_time
        FROM document
        WHERE document_id = {document_id}
    """

    rows = exesql(sql)
    return rows[0]


def get_all_kb_ids(kb_id):
    kbs = [kb_id]
    sql = f"select knowledge_base_id from knowledge_base where up_id = '{kb_id}'"
    rows = exesql(sql)
    for row in rows:
        kbs.extend(get_all_kb_ids(row['knowledge_base_id']))
    return kbs


# -----------------------------
# 获取切片的余弦值（可加条件）
# -----------------------------
def get_chunk_cosine(
        query_vector,
        knowledge_base_id=None,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 90
) -> List[Dict[str, Any]]:
    # 构建 WHERE 子句和参数
    where_clause = " WHERE 1=1 AND "
    params = []

    if filters:
        for k, v in filters.items():
            if v is not None and v != '':
                where_clause += f" AND {k} = ?"
                params.append(v)

    # 输入知识库需要查询所有下级知识库
    if knowledge_base_id is not None and knowledge_base_id != '':
        kb_ids = get_all_kb_ids(knowledge_base_id)
        where_clause += " knowledge_base_id in " + "[" + ",".join(f"'{x}'" for x in kb_ids) + "]"

    # query_vector 作为参数传入
    params.append(query_vector[0])
    params.append(top_k)

    sql = f"""
    WITH chunks AS (
        SELECT
            document_id,
            file_name,
            location_path,
            UNNEST(file_name_vector) AS chunk_vector,
            UNNEST(generate_series(0, len(file_content_chunks_vector) - 1)) AS chunk_index
        FROM document
        {where_clause}
        AND file_content_chunks_vector IS NOT NULL
        AND len(file_content_chunks_vector) > 0
    ),
    similarities AS (
        SELECT
            document_id,
            file_name,
            location_path,
            chunk_index,
            chunk_vector,
            cosine_similarity(chunk_vector, CAST(? AS FLOAT[])) AS cosine_similarity
        FROM chunks
        WHERE chunk_vector IS NOT NULL
    )
    SELECT
        document_id,
        file_name,
        location_path,
        chunk_index,
        chunk_vector,
        cosine_similarity
    FROM similarities
    ORDER BY cosine_similarity DESC
    LIMIT ?;
    """

    rows = exesql(sql, params)
    return [dict(row) for row in rows]


# -----------------------------
# 获取文件名的余弦值（可加条件）
# -----------------------------
def get_file_name_cosine(
        query_vector,
        knowledge_base_id = None,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 90
) -> List[Dict[str, Any]]:
    # 构建 WHERE 子句和参数
    where_clause = " WHERE 1=1 AND "
    params = []

    if filters:
        for k, v in filters.items():
            if v is not None and v != '':
                where_clause += f" AND {k} = ?"
                params.append(v)

    # 输入知识库需要查询所有下级知识库
    if knowledge_base_id is not None and knowledge_base_id != '':
        kb_ids = get_all_kb_ids(knowledge_base_id)
        where_clause += " knowledge_base_id in " + "[" + ",".join(f"'{x}'" for x in kb_ids) + "]"

    # query_vector 作为参数传入
    params.append(query_vector[0])
    params.append(top_k)

    sql = f"""
    WITH chunks AS (
        SELECT
            document_id,
            file_name,
            location_path,
            UNNEST(file_name_vector) AS chunk_vector,
            UNNEST(generate_series(0, len(file_name_vector) - 1)) AS chunk_index
        FROM document
        {where_clause}
        AND file_name_vector IS NOT NULL
        AND len(file_name_vector) > 0
    ),
    similarities AS (
        SELECT
            document_id,
            file_name,
            location_path,
            cosine_similarity(chunk_vector, CAST(? AS FLOAT[])) AS cosine_similarity
        FROM chunks
        WHERE chunk_vector IS NOT NULL
    )
    SELECT
        document_id,
        file_name,
        location_path,
        cosine_similarity
    FROM similarities
    ORDER BY cosine_similarity DESC
    LIMIT ?;
    """

    rows = exesql(sql, params)
    return [dict(row) for row in rows]

