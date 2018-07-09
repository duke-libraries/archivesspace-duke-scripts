SELECT
    YEAR(accession.accession_date) AS 'Year',
    QUARTER(accession.accession_date) AS 'Quarter',
    COUNT(*) AS 'Total accessions measured in linear feet',
    COUNT(CASE
        WHEN accession.identifier LIKE '%ua%' THEN 1
        ELSE NULL
    END) AS Count_UAAccessions,
    ROUND(SUM(CASE
                WHEN accession.identifier LIKE '%ua%' THEN extent.number
                ELSE 0
            END),
            2) AS 'UA Linear feet',
    COUNT(CASE
        WHEN accession.identifier NOT LIKE '%ua%' THEN 1
        ELSE NULL
    END) AS Count_OtherAccessions,
    ROUND(SUM(CASE
                WHEN accession.identifier NOT LIKE '%ua%' THEN extent.number
                ELSE 0
            END),
            2) AS 'Other Linear feet',
    ROUND(SUM(extent.number), 2) AS 'Total Linear feet'
FROM
    accession
        LEFT JOIN
    extent ON accession.id = extent.accession_id
WHERE
    (extent_type_id IN (SELECT 
            id
        FROM
            enumeration_value
        WHERE
            LOWER(value) LIKE '%linear%'))
        AND repo_id = 2
        AND accession.accession_date >= '20170701'
        AND accession.accession_date <= '20180631'
GROUP BY Quarter(accession.accession_date)
ORDER BY YEAR, Quarter