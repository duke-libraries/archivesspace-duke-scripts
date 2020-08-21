SELECT
    accession.id,
    accession.identifier,
    accession.title,
    accession.accession_date,
    extent.number,
    ev4.value AS extent_type,
    REPLACE(REPLACE(REPLACE(extent.container_summary, '\r', ''), '\n', ''), '\t','') AS container_summary,
    ev3.value AS acquisition_type,
    ev2.value AS research_center,
    ev1.value AS primary_collector,
    name_corporate_entity.sort_name AS 'center_heading',
    REPLACE(REPLACE(REPLACE(accession.content_description, '\r', ''), '\n', ''), '\t','') AS content_description,
    REPLACE(REPLACE(REPLACE(accession.inventory, '\r', ''), '\n', ''), '\t','') AS inventory,
    REPLACE(REPLACE(REPLACE(accession.provenance, '\r', ''), '\n', ''), '\t','') AS provenance,
    REPLACE(REPLACE(REPLACE(accession.general_note, '\r', ''), '\n', ''), '\t','') AS general_note,
    REPLACE(REPLACE(REPLACE(accession.access_restrictions_note, '\r', ''), '\n', ''), '\t','') AS access_restrictions_note,
    REPLACE(REPLACE(REPLACE(accession.use_restrictions_note, '\r', ''), '\n', ''), '\t','') AS use_restrictions_note,
    user_defined.real_1 AS 'appraisal_value',
    (CASE
        WHEN user_defined.boolean_2 <> 0 THEN 'yes'
        ELSE 'no'
    END) AS 'ready_for_ts?',
    (CASE
        WHEN user_defined.boolean_1 <> 0 THEN 'yes'
        ELSE 'no'
    END) AS 'electronic media',
    user_defined.integer_1 AS 'aleph_order_number',
    accession.created_by,
    ev5.value AS processing_priority,
    ev6.value AS processing_status,
    collection_management.processing_hours_total AS 'total_processing_hours'
FROM
    accession
        LEFT JOIN
    collection_management ON accession.id = collection_management.accession_id
        LEFT JOIN
    user_defined ON accession.id = user_defined.accession_id
        LEFT JOIN
    enumeration_value ev2 ON user_defined.enum_2_id = ev2.id
        LEFT JOIN
    enumeration_value ev3 ON accession.acquisition_type_id = ev3.id
        LEFT JOIN
    enumeration_value ev1 ON user_defined.enum_1_id = ev1.id
        LEFT JOIN
    extent ON accession.id = extent.accession_id
        LEFT JOIN
    enumeration_value ev4 ON extent.extent_type_id = ev4.id
        LEFT JOIN
    enumeration_value ev5 ON collection_management.processing_priority_id = ev5.id
        LEFT JOIN
    enumeration_value ev6 ON collection_management.processing_status_id = ev6.id
		LEFT JOIN
	linked_agents_rlshp on accession.id = linked_agents_rlshp.accession_id 
		LEFT JOIN
	agent_corporate_entity on linked_agents_rlshp.agent_corporate_entity_id = agent_corporate_entity.id
		LEFT JOIN
	name_corporate_entity on agent_corporate_entity.id = name_corporate_entity.agent_corporate_entity_id
WHERE
        repo_id = 2
        AND (ev2.value = 'ada' 
        OR ev1.value = '[primary collector name]'
        OR name_corporate_entity.sort_name like '%Archive of Documentary Arts%')
GROUP BY accession.identifier
ORDER BY accession.identifier;
