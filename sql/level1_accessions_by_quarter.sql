SELECT
    YEAR(accession.accession_date) AS 'Year',
    QUARTER(accession.accession_date) AS 'Quarter',
    COUNT(*) AS 'Count of accessions processed to Level 1',
    COUNT(CASE
        WHEN accession.identifier LIKE '%ua%' THEN 1
        ELSE NULL
    END) AS Count_UAAccessions,
    ROUND(SUM(CASE
                WHEN accession.identifier LIKE '%ua%' THEN extent.number
                ELSE 0
            END),
            2) AS 'UA Level 1 Linear feet',
    COUNT(CASE
        WHEN accession.identifier NOT LIKE '%ua%' THEN 1
        ELSE NULL
    END) AS Count_RLAccessions,
    ROUND(SUM(CASE
                WHEN accession.identifier NOT LIKE '%ua%' THEN extent.number
                ELSE 0
            END),
            2) AS 'RL Level 1 Linear feet',
    ROUND(SUM(extent.number), 2) AS 'Total L1 Linear feet'
FROM
    accession
        LEFT JOIN
    extent ON accession.id = extent.accession_id
		LEFT JOIN
	collection_management ON accession.id = collection_management.accession_id
WHERE
    (extent_type_id IN (SELECT 
            id
        FROM
            enumeration_value
        WHERE
            LOWER(value) LIKE '%linear%'))
        AND repo_id = 2
        AND accession.accession_date >= '20180701'
        AND accession.accession_date <= '20190631'
        /* Where processing status = completed_level1_accessioned*/
        AND collection_management.processing_status_id = 61145
GROUP BY Quarter(accession.accession_date)
ORDER BY YEAR, Quarter
