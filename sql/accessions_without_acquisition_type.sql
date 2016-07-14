SELECT 
    accession.identifier,
    accession.title,
    value AS 'Acquisition type'
FROM
    accession
        LEFT JOIN
    extent ON accession.id = extent.accession_id
        LEFT JOIN
    enumeration_value ON acquisition_type_id = enumeration_value.id
WHERE
	value is NULL
    AND repo_id = 2
	AND accession.accession_date >= '20150701'
    AND accession.accession_date <= '20160631'