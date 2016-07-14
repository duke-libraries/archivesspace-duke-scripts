SELECT 
    accession.identifier,
    accession.title,
    extent.number,
    enumeration_value.value
FROM
    accession
        LEFT JOIN
    extent ON accession.id = extent.accession_id
        LEFT JOIN
    enumeration_value ON extent.extent_type_id = enumeration_value.id
WHERE
    repo_id = 2
	AND accession.accession_date >= '20150701'
    AND accession.accession_date <= '20160631'
    AND NOT enumeration_value.value LIKE '%linear%'