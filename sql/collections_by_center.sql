SELECT
    resource.id as 'aspace_resource_id',
    replace(replace(replace(replace(replace(resource.identifier, ',', '.'), '"', ''), ']', ''), '[', ''), '.null', '') as collection_id,
    resource.title,
    extent.number as 'extent_number',
    ev1.value AS 'extent_type',
    extent.container_summary,
    resource.ead_id,
    resource.ead_location as 'finding_aid_url',
    resource.finding_aid_note,
    resource.repository_processing_note,
    resource.finding_aid_date,
    resource.finding_aid_author,
    resource.created_by,
    resource.last_modified_by,
    resource.system_mtime,
    name_corporate_entity.sort_name as "center_heading"
FROM
    resource
        LEFT JOIN
    extent on resource.id = extent.resource_id
        LEFT JOIN
    enumeration_value ev1 ON extent.extent_type_id = ev1.id
		LEFT JOIN
	linked_agents_rlshp on resource.id = linked_agents_rlshp.resource_id 
		LEFT JOIN
	agent_corporate_entity on linked_agents_rlshp.agent_corporate_entity_id = agent_corporate_entity.id
		LEFT JOIN
	name_corporate_entity on agent_corporate_entity.id = name_corporate_entity.agent_corporate_entity_id
WHERE
    resource.repo_id = 2
    AND
    name_corporate_entity.sort_name like "%Archive of Documentary Art%"
GROUP BY resource.id
ORDER BY
    resource.identifier;
