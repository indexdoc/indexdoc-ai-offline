import logging
import time

from database.duckdb_config import duckdb_config
from database.duckdb_queue import DuckDBQueue
import duckdb

# 全局实例
duckdb_queue = DuckDBQueue(default_timeout=30)
duckdb_queue.start()

def is_read_query(sql: str) -> bool:
    """简单判断是否为只读查询"""
    upper_sql = sql.strip().upper()
    if upper_sql.startswith(("SELECT", "PRAGMA")):
        return True
    if upper_sql.startswith("WITH"):
        return " INSERT " not in upper_sql and " UPDATE " not in upper_sql and " DELETE " not in upper_sql
    write_keywords = {"INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "REPLACE", "MERGE"}
    return not any(kw in upper_sql for kw in write_keywords)

def direct_exesql(sql, params):
    conn = duckdb.connect(database=duckdb_config['database'])
    try:
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return result
    except Exception as e:
        if "closed" in str(e):
            raise TimeoutError("Query timed out and connection was closed")
        raise
    finally:
        conn.close()  # 确保关闭

def exesql(sql: str, params=None, timeout=None,is_many_insert=False ):
    _time_begin = time.time()
    logging.debug('duckdb sql %f: %s' % (_time_begin, sql))
    logging.debug('duckdb sql %f: params:%s' % (_time_begin, str(params)))
    try:
        if is_read_query(sql):
            rts = direct_exesql(sql, params)
        else:
            rts = duckdb_queue.submit_task(sql, params, timeout, is_many_insert)
        logging.debug('duckdb sql %f success: count %d, time %f ' % (
            _time_begin, len(rts) if rts is not None and not isinstance(rts, int) else 0, time.time() - _time_begin))
        return rts
    except Exception as e:
        logging.error('duckdb sql %f fail:%s' % (_time_begin, str(e)))
        # logging.error(traceback.format_exc())
        raise e
    finally:
        pass
