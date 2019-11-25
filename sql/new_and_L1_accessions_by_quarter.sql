/*Generates Quarterly counts and linear foot totals of accessions measured in linear feet for UA and RL, with grand totals)*/
SELECT 
    YEAR(accession.accession_date) AS 'Year',
    QUARTER(accession.accession_date) AS 'Quarter',
    COUNT(CASE
        WHEN
            (accession.identifier LIKE '%ua%'
                AND collection_management.processing_status_id = 61153)
        THEN
            1
        ELSE NULL
    END) AS 'UA New-Unprocessed Count',
    ROUND(SUM(CASE
                WHEN
                    (accession.identifier LIKE '%ua%'
                        AND collection_management.processing_status_id = 61153)
                THEN
                    extent.number
                ELSE 0
            END),
            2) AS 'UA New-Unprocessed LF',
    COUNT(CASE
        WHEN
            (accession.identifier LIKE '%ua%'
                AND collection_management.processing_status_id = 61145)
        THEN
            1
        ELSE NULL
    END) AS 'UA L1 Count',
    ROUND(SUM(CASE
                WHEN
                    (accession.identifier LIKE '%ua%'
                        AND collection_management.processing_status_id = 61145)
                THEN
                    extent.number
                ELSE 0
            END),
            2) AS 'UA L1 LF',
    COUNT(CASE
        WHEN
            (accession.identifier NOT LIKE '%ua%'
                AND collection_management.processing_status_id = 61153)
        THEN
            1
        ELSE NULL
    END) AS 'RL New-Unprocessed Count',
    ROUND(SUM(CASE
                WHEN
                    (accession.identifier NOT LIKE '%ua%'
                        AND collection_management.processing_status_id = 61153)
                THEN
                    extent.number
                ELSE 0
            END),
            2) AS 'RL New-Unprocessed LF',
    COUNT(CASE
        WHEN
            (accession.identifier NOT LIKE '%ua%'
                AND collection_management.processing_status_id = 61145)
        THEN
            1
        ELSE NULL
    END) AS 'RL L1 Count',
    ROUND(SUM(CASE
                WHEN
                    (accession.identifier NOT LIKE '%ua%'
                        AND collection_management.processing_status_id = 61145)
                THEN
                    extent.number
                ELSE 0
            END),
            2) AS 'RL L1 LF',
    COUNT(CASE
        WHEN collection_management.processing_status_id = 61153 THEN 1
        ELSE NULL
    END) AS 'Total New-Unprocessed Count',
    ROUND(SUM(CASE
                WHEN collection_management.processing_status_id = 61153 THEN extent.number
                ELSE 0
            END),
            2) AS 'Total New-Unprocessed LF',
    COUNT(CASE
        WHEN collection_management.processing_status_id = 61145 THEN 1
        ELSE NULL
    END) AS 'Total L1 Count',
    ROUND(SUM(CASE
                WHEN collection_management.processing_status_id = 61145 THEN extent.number
                ELSE 0
            END),
            2) AS 'Total L1 LF',
    COUNT(*) AS 'Total Accessions Count (New and L1)',
    ROUND(SUM(extent.number), 2) AS 'Total LF (New and L1)'
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
        AND (collection_management.processing_status_id = 61145
        OR collection_management.processing_status_id = 61153)
GROUP BY QUARTER(accession.accession_date)
ORDER BY YEAR , Quarter
