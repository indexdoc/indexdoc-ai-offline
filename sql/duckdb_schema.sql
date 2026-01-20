-- DuckDB数据库结构导出（按执行顺序排列）
-- 导出时间: 2025-11-01 09:26:11
-- 此文件可直接执行以重建数据库结构

-- === 表结构 ===

-- 表: main.chat
CREATE TABLE main.chat (chat_id BIGINT NOT NULL, customer_id VARCHAR NULL, chat_name VARCHAR NULL, chat_type VARCHAR NULL, create_time TIMESTAMP WITH TIME ZONE NULL, extend_attrs VARCHAR NULL, PRIMARY KEY (chat_id));

-- 表: main.chat_history
CREATE TABLE main.chat_history (chat_history_id BIGINT NOT NULL, chat_id BIGINT NULL, chat_index VARCHAR NULL, role_name VARCHAR NULL, message VARCHAR NULL, create_time TIMESTAMP WITH TIME ZONE NULL, extend_attrs VARCHAR NULL, PRIMARY KEY (chat_history_id));

-- 表: main.document
CREATE TABLE main.document (document_id BIGINT NOT NULL, document_uuid VARCHAR NULL, knowledge_base_id VARCHAR NULL, file_name VARCHAR NULL, knowledge_name VARCHAR NULL, file_type VARCHAR NULL, metadata VARCHAR NULL, location_path VARCHAR NULL, file_summary VARCHAR NULL, file_content VARCHAR NULL, file_content_chunks VARCHAR[] NULL, file_name_vector DOUBLE[][] NULL, file_summary_vector DOUBLE[][] NULL, file_content_vector DOUBLE[][] NULL, file_content_chunks_vector DOUBLE[][] NULL, file_size INTEGER NULL, file_timestamp INTEGER NULL, kb_load_state VARCHAR NULL, markdown VARCHAR NULL, extend_attrs VARCHAR NULL, order_no VARCHAR NULL, create_time TIMESTAMP WITH TIME ZONE NULL, PRIMARY KEY (document_id));

-- 表: main.knowledge_base
CREATE TABLE main.knowledge_base (knowledge_base_id BIGINT NOT NULL, up_id VARCHAR NULL, knowledge_base_name VARCHAR NULL, location_path VARCHAR NULL, kb_load_state VARCHAR NULL, extend_attrs VARCHAR NULL, order_no VARCHAR NULL, description VARCHAR NULL, create_time TIMESTAMP WITH TIME ZONE NULL DEFAULT now(), is_deleted VARCHAR NULL, PRIMARY KEY (knowledge_base_id));

-- === 视图 ===

-- 视图: main.view_kb_doc
CREATE VIEW view_kb_doc AS (SELECT knowledge_base_id, CAST(up_id AS VARCHAR) AS up_id, knowledge_base_name AS "name", NULL AS document_id, NULL AS lc_file_id, knowledge_base_id AS lc_kb_id, NULL AS metadata, NULL AS file_size, NULL AS file_timestamp, kb_load_state, location_path FROM knowledge_base) UNION ALL (SELECT NULL AS knowledge_base_id, CAST(knowledge_base_id AS VARCHAR) AS up_id, file_name AS "name", document_id, document_id AS lc_file_id, knowledge_base_id AS lc_kb_id, metadata AS metadata, file_size, file_timestamp, kb_load_state, location_path FROM "document");;

