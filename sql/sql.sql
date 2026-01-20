CREATE or replace VIEW view_kb_doc AS (
SELECT
	knowledge_base_id,
	CAST(up_id AS VARCHAR) AS up_id,
	knowledge_base_name AS "name",
	NULL AS document_id,
	NULL AS lc_file_id,
	knowledge_base_id AS lc_kb_id,
	NULL AS metadata,
	NULL AS file_size,
	NULL AS file_timestamp,
	kb_load_state,
	location_path
FROM
	knowledge_base order by location_path
)
UNION ALL (
SELECT
    NULL AS knowledge_base_id,
    CAST(knowledge_base_id AS VARCHAR) AS up_id,
    file_name AS "name",
    document_id,
    document_id AS lc_file_id,
    knowledge_base_id AS lc_kb_id,
    metadata AS metadata,
    file_size,
    file_timestamp,
    kb_load_state,
    location_path
FROM
    "document" order by location_path
);