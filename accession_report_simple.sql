SELECT 
    accession.identifier,
    accession.title,
    accession_date,
    extent.number AS 'extent_number',
    enumeration_value.value AS 'extent_unit',
    extent.container_summary,
    accession.content_description,
    accession.access_restrictions_note,
    accession.use_restrictions_note,
    accession.acquisition_type_id,
    accession.created_by,
    name_corporate_entity.sort_name AS 'research_center',
    user_defined.real_1 as 'appraisal_value',
    (case when user_defined.boolean_2 <> 0 then "yes" else "no" end) as 'ready_for_ts?',
    (case when user_defined.boolean_1 <> 0 then "yes" else "no" end) as 'electronic media',
    user_defined.integer_1 as 'aleph_order_number'
FROM
    accession
		left join
	user_defined on accession.id = user_defined.accession_id
        LEFT JOIN
    linked_agents_rlshp ON accession.id = linked_agents_rlshp.accession_id
        LEFT JOIN
    name_corporate_entity ON linked_agents_rlshp.agent_corporate_entity_id = name_corporate_entity.agent_corporate_entity_id
        LEFT JOIN
    extent ON accession.id = extent.accession_id
        LEFT JOIN
    enumeration_value ON extent.extent_type_id = enumeration_value.id
WHERE
    accession.accession_date >= '20150701'
        AND accession.accession_date <= '20160631'
        AND repo_id = 2;
