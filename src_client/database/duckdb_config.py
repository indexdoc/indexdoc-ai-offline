import frozen_support
database_file = frozen_support.get_user_database_path()
duckdb_config = {
    'database': database_file,
    'kb_table': 'knowledge_base',
    'file_table': 'document',
}
