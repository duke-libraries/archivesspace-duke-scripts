SELECT 
    enumeration_value.value AS 'Research Center',
    COUNT(*) AS 'Total accessions measured in linear feet',
    ROUND(SUM(extent.number), 2) AS 'Linear feet'
FROM
    accession
        LEFT JOIN
    extent ON accession.id = extent.accession_id
		left join
	user_defined on accession.id = user_defined.accession_id
        LEFT JOIN
    enumeration_value ON user_defined.enum_2_id = enumeration_value.id
WHERE
    (extent_type_id IN (SELECT 
            id
        FROM
            enumeration_value
        WHERE
            LOWER(value) LIKE '%linear%'))
        AND repo_id = 2
        AND accession.accession_date >= '20150701'
        AND accession.accession_date <= '20160631'
GROUP BY enumeration_value.value;