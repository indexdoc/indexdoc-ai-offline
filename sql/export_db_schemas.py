import sqlite3
import duckdb
import os
from datetime import datetime


# ----------------------
# 导出数据库结构到SQL文件
# ----------------------

def export_sqlite_schema(db_path, output_sql_path):
    """导出SQLite数据库结构，确保表先于索引"""
    if not os.path.exists(db_path):
        print(f"错误：SQLite数据库文件不存在 - {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 获取所有表
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()

        if not tables:
            print("SQLite数据库中没有找到用户创建的表")
            return True

        with open(output_sql_path, 'w', encoding='utf-8') as f:
            f.write("-- SQLite数据库表结构导出（按执行顺序排列）\n")
            f.write(f"-- 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- 此文件可直接执行以重建数据库结构\n\n")

            # 1. 先导出所有表结构
            print("导出SQLite表结构...")
            f.write("-- === 表结构 ===\n\n")
            for (table_name,) in tables:
                print(f"  表: {table_name}")

                # 写入表创建语句
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                create_stmt = cursor.fetchone()[0]
                f.write(f"-- 表: {table_name}\n")
                f.write(f"{create_stmt};\n\n")

            # 2. 再导出所有索引（确保表已创建）
            print("导出SQLite索引...")
            f.write("-- === 索引 ===\n\n")
            for (table_name,) in tables:
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}'")
                indexes = cursor.fetchall()

                for (index_sql,) in indexes:
                    if index_sql:
                        index_name = index_sql.split()[2].strip('"')
                        print(f"  索引: {index_name} (表: {table_name})")
                        f.write(f"-- 表 {table_name} 的索引\n")
                        f.write(f"{index_sql};\n\n")

        print(f"SQLite结构已导出到: {output_sql_path}")
        return True

    except Exception as e:
        print(f"导出SQLite结构时出错: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()


def export_duckdb_schema(db_path, output_sql_path):
    """导出DuckDB数据库结构，确保表先于视图"""
    if not os.path.exists(db_path):
        print(f"错误：DuckDB数据库文件不存在 - {db_path}")
        return False

    try:
        conn = duckdb.connect(db_path)

        # 获取所有表（按名称排序）
        tables = conn.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_type = 'BASE TABLE' 
              AND table_schema NOT IN ('information_schema', 'sys')
            ORDER BY table_schema, table_name
        """).fetchall()

        # 获取所有视图（按名称排序）
        views = conn.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_type = 'VIEW' 
              AND table_schema NOT IN ('information_schema', 'sys')
            ORDER BY table_schema, table_name
        """).fetchall()

        if not tables and not views:
            print("DuckDB数据库中没有找到用户创建的表或视图")
            return True

        with open(output_sql_path, 'w', encoding='utf-8') as f:
            f.write("-- DuckDB数据库结构导出（按执行顺序排列）\n")
            f.write(f"-- 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- 此文件可直接执行以重建数据库结构\n\n")

            # 1. 先导出所有表结构
            if tables:
                print("导出DuckDB表结构...")
                f.write("-- === 表结构 ===\n\n")
                for schema, table_name in tables:
                    full_name = f"{schema}.{table_name}"
                    print(f"  表: {full_name}")

                    # 获取表结构信息
                    columns = conn.execute(f"""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns
                        WHERE table_schema = '{schema}' AND table_name = '{table_name}'
                        ORDER BY ordinal_position
                    """).fetchall()

                    # 构建CREATE TABLE语句
                    column_defs = []
                    for col_name, data_type, is_nullable, default_val in columns:
                        nullable = "NULL" if is_nullable == 'YES' else "NOT NULL"
                        default_clause = f" DEFAULT {default_val}" if default_val else ""
                        column_defs.append(f"{col_name} {data_type} {nullable}{default_clause}")

                    # 检查主键
                    pk_columns = conn.execute(f"""
                        SELECT kcu.column_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                        WHERE tc.table_schema = '{schema}' 
                          AND tc.table_name = '{table_name}'
                          AND tc.constraint_type = 'PRIMARY KEY'
                        ORDER BY kcu.ordinal_position
                    """).fetchall()

                    if pk_columns:
                        pk_cols = ", ".join([col[0] for col in pk_columns])
                        column_defs.append(f"PRIMARY KEY ({pk_cols})")

                    create_stmt = f"CREATE TABLE {full_name} ({', '.join(column_defs)})"
                    f.write(f"-- 表: {full_name}\n")
                    f.write(f"{create_stmt};\n\n")

            # 2. 再导出所有视图（确保依赖的表已创建）
            if views:
                print("导出DuckDB视图...")
                f.write("-- === 视图 ===\n\n")
                for schema, view_name in views:
                    full_name = f"{schema}.{view_name}"
                    print(f"  视图: {full_name}")

                    # 获取视图定义
                    view_def = conn.execute(f"""
                        SELECT view_definition 
                        FROM information_schema.views 
                        WHERE table_schema = '{schema}' AND table_name = '{view_name}'
                    """).fetchone()[0]

                    # 处理视图定义
                    if not view_def.strip().upper().startswith("CREATE VIEW"):
                        view_def = f"CREATE VIEW {full_name} AS {view_def}"
                    f.write(f"-- 视图: {full_name}\n")
                    f.write(f"{view_def};\n\n")

        print(f"DuckDB结构已导出到: {output_sql_path}")
        return True

    except Exception as e:
        print(f"导出DuckDB结构时出错: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()


# ----------------------
# 从SQL文件创建新数据库
# ----------------------

def create_sqlite_from_sql(sql_file_path, db_path):
    """根据SQL结构文件创建新的SQLite数据库"""
    if not os.path.exists(sql_file_path):
        print(f"错误：SQL文件不存在 - {sql_file_path}")
        return False

    # 如果目标数据库已存在，先删除
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"已删除现有SQLite数据库: {db_path}")
        except Exception as e:
            print(f"删除SQLite数据库时出错: {str(e)}")
            return False

    try:
        # 连接到新数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 读取SQL文件内容
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = ''
            for linestr in f:  # 这里将f.readline()改为f，实现迭代读取所有行
                # 去除首尾空白后，如果不是以--开头的注释行，则保留
                stripped_line = linestr.strip()
                if not stripped_line.startswith('--') and stripped_line:
                    sql_content += linestr
        # 分割SQL语句（处理分号分隔的语句）
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if
                          stmt.strip() and not stmt.strip().startswith('--')]

        # 执行每个SQL语句
        for i, stmt in enumerate(sql_statements):
            try:
                cursor.execute(stmt)
                # 提取表名或索引名用于显示
                if stmt.strip().upper().startswith('CREATE TABLE'):
                    table_name = stmt.split()[2].split('(')[0].strip('"').strip("'")
                    print(f"已创建SQLite表: {table_name}")
                elif stmt.strip().upper().startswith('CREATE INDEX'):
                    index_name = stmt.split()[2].strip('"').strip("'")
                    print(f"已创建SQLite索引: {index_name}")
            except Exception as e:
                print(f"执行SQL语句 {i + 1} 时出错: {str(e)}")
                print(f"出错的SQL语句: {stmt[:100]}...")
                conn.rollback()
                return False

        # 提交事务
        conn.commit()
        print(f"SQLite数据库已成功创建: {db_path}")
        return True

    except Exception as e:
        print(f"创建SQLite数据库时出错: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()


def create_duckdb_from_sql(sql_file_path, db_path, verify=True):
    """
    根据SQL结构文件创建新的DuckDB数据库，并可选验证创建结果
    """
    if not os.path.exists(sql_file_path):
        print(f"错误：SQL文件不存在 - {sql_file_path}")
        return False

    # 如果目标数据库已存在，先删除
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"已删除现有DuckDB数据库: {db_path}")
        except Exception as e:
            print(f"删除DuckDB数据库时出错: {str(e)}")
            return False

    try:
        # 连接到新数据库
        conn = duckdb.connect(db_path)
        print(f"已连接到DuckDB数据库: {db_path}")

        # 读取SQL文件内容
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # 分割SQL语句（更健壮的分割方式）
        statements = []
        current_stmt = []
        in_string = False
        string_char = None

        for line in sql_content.split('\n'):
            # 忽略注释行
            if line.strip().startswith('--'):
                continue

            for c in line:
                # 处理字符串中的分号
                if c in ["'", '"']:
                    if in_string and c == string_char:
                        in_string = False
                        string_char = None
                    elif not in_string:
                        in_string = True
                        string_char = c

                # 分号作为语句结束符，但不在字符串中
                if c == ';' and not in_string:
                    statements.append(''.join(current_stmt).strip())
                    current_stmt = []
                else:
                    current_stmt.append(c)

        # 添加最后一个语句
        if current_stmt:
            statements.append(''.join(current_stmt).strip())

        print(f"成功解析 {len(statements)} 条SQL语句")

        # 执行每个SQL语句
        executed = 0
        for i, stmt in enumerate(statements):
            if not stmt:
                continue

            try:
                # 执行语句并获取结果
                result = conn.execute(stmt)
                executed += 1

                # 识别执行的对象类型
                stmt_upper = stmt.strip().upper()
                if stmt_upper.startswith('CREATE TABLE'):
                    table_name = stmt.split()[2].split('(')[0].strip('"').strip("'")
                    print(f"执行成功 [{i + 1}/{len(statements)}]: 创建表 {table_name}")
                elif stmt_upper.startswith('CREATE VIEW'):
                    view_name = stmt.split()[2].split('AS')[0].strip('"').strip("'")
                    print(f"执行成功 [{i + 1}/{len(statements)}]: 创建视图 {view_name}")
                else:
                    print(f"执行成功 [{i + 1}/{len(statements)}]: 其他SQL语句")

            except Exception as e:
                print(f"执行失败 [{i + 1}/{len(statements)}]: {str(e)}")
                print(f"出错的SQL语句: {stmt[:200]}...")
                # 继续执行其他语句，而不是立即返回
                # return False

        print(f"SQL语句执行完成，共 {executed}/{len(statements)} 条成功执行")

        # 验证创建结果
        if verify:
            print("\n开始验证创建结果...")
            # 获取所有表
            tables = conn.execute("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_type = 'BASE TABLE' 
                  AND table_schema NOT IN ('information_schema', 'sys')
            """).fetchall()

            # 获取所有视图
            views = conn.execute("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_type = 'VIEW' 
                  AND table_schema NOT IN ('information_schema', 'sys')
            """).fetchall()

            print(f"验证结果: 发现 {len(tables)} 个表，{len(views)} 个视图")

            if len(tables) == 0 and len(views) == 0:
                print("警告：未发现任何表或视图，可能所有SQL语句都未执行成功")
            else:
                if len(tables) > 0:
                    print("已创建的表:")
                    for schema, name in tables:
                        print(f"  - {schema}.{name}")
                if len(views) > 0:
                    print("已创建的视图:")
                    for schema, name in views:
                        print(f"  - {schema}.{name}")

        print(f"\nDuckDB数据库操作完成: {db_path}")
        return True

    except Exception as e:
        print(f"创建DuckDB数据库时出错: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()


# ----------------------
# 主函数
# ----------------------

if __name__ == "__main__":
    # 配置文件路径
#    sqlite_db_path = "../database/info.db"  # SQLite源数据库路径
    duckdb_db_path = "../database/default.duck"  # DuckDB源数据库路径

#    sqlite_sql_path = "sqlite_schema.sql"  # SQLite导出SQL路径
    duckdb_sql_path = "duckdb_schema.sql"  # DuckDB导出SQL路径

#    new_sqlite_db = "info.db"  # 新SQLite数据库路径
    new_duckdb_db = "default.duck"  # 新DuckDB数据库路径

    # 步骤1: 导出数据库结构到SQL文件
    print("===== 开始导出数据库结构 =====")
 #   export_sqlite_schema(sqlite_db_path, sqlite_sql_path)
    export_duckdb_schema(duckdb_db_path, duckdb_sql_path)

    # 步骤2: 从SQL文件创建新数据库
    print("\n===== 开始从SQL文件创建新数据库 =====")
#    create_sqlite_from_sql(sqlite_sql_path, new_sqlite_db)
    create_duckdb_from_sql(duckdb_sql_path, new_duckdb_db)

    print("\n所有操作完成")


