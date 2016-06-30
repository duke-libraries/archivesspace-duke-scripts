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
    user_defined.real_1 as 'appraisal_value',
    (case when user_defined.boolean_2 <> 0 then "yes" else "no" end) as 'ready_for_ts?',
    (case when user_defined.boolean_1 <> 0 then "yes" else "no" end) as 'electronic media',
    user_defined.integer_1 as 'aleph_order_number',
    accession.created_by
FROM
    accession
        left JOIN
    user_defined ON accession.id = user_defined.accession_id
		left JOIN
    enumeration_value ev2 ON user_defined.enum_2_id = ev2.id
		left JOIN
	enumeration_value ev3 ON accession.acquisition_type_id = ev3.id
		left JOIN
	enumeration_value ev1 ON user_defined.enum_1_id = ev1.id
        left JOIN
    extent ON accession.id = extent.accession_id
		left join
	enumeration_value ev4 on extent.extent_type_id = ev4.id
WHERE
    accession.accession_date >= '20150701'
        AND accession.accession_date <= '20160631'
        AND repo_id = 2
order by
	accession.identifier;