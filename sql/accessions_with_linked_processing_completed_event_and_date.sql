SELECT 
    accession.title,
    accession.identifier,
    extent.number,
    enumeration_value.value AS 'extent_type',
    ev1.value AS processing_status,
    ev2.value AS event_type,
    date.begin as 'event_date'
FROM
    accession
        LEFT JOIN
    extent ON accession.id = extent.accession_id
        LEFT JOIN
    enumeration_value ON extent_type_id = enumeration_value.id
		LEFT JOIN
	collection_management ON accession.id = collection_management.accession_id
		LEFT JOIN
	enumeration_value ev1 ON collection_management.processing_status_id = ev1.id
		LEFT JOIN
	event_link_rlshp ON accession.id = event_link_rlshp.accession_id
		LEFT JOIN
	event ON event_link_rlshp.event_id = event.id
		LEFT JOIN
	enumeration_value ev2 ON event.event_type_id = ev2.id
		LEFT JOIN
	date ON event.id = date.event_id
WHERE
    LOWER(enumeration_value.value) LIKE '%linear%'
        AND accession.repo_id = 2
        AND LOWER(ev2.value) LIKE '%cataloged%'
        AND date.begin >= '2015-07-01'
        AND date.begin <= '2016-06-30'