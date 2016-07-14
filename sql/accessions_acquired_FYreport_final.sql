SELECT 
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
    accession.created_by
FROM
    accession
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
WHERE
    accession.accession_date >= '20150701'
        AND accession.accession_date <= '20160631'
        AND repo_id = 2
ORDER BY accession.identifier;
