SELECT
    accession.id,
    accession.identifier,
    accession.title,
    accession.accession_date,
    extent.number,
    ev4.value AS extent_type,
    extent.container_summary,
    ev3.value AS acquisition_type,
    ev2.value AS research_center,
    ev1.value AS primary_collector,
    accession.content_description,
    accession.access_restrictions_note,
    accession.use_restrictions_note,
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
    collection_management.processing_hours_total AS 'total_processing_hours',
    spawned_rlshp.resource_id as 'related_resource_id',
    resource.title as 'related_resource_title'
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
    spawned_rlshp ON accession.id = spawned_rlshp.accession_id
        LEFT JOIN
    resource ON spawned_rlshp.resource_id = resource.id 
WHERE
    accession.repo_id = 2
ORDER BY 
    accession.id
