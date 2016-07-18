SELECT 
    COUNT(*) AS 'Total accessions in linear feet',
    COUNT(CASE
        WHEN accession.identifier LIKE '%ua%' THEN 1
        ELSE NULL
    END) AS UAAccessions,
    COUNT(CASE
        WHEN accession.identifier NOT LIKE '%ua%' THEN 1
        ELSE NULL
    END) AS OtherAccessions
FROM
    accession
WHERE
    repo_id = 2
        AND accession.accession_date >= '20150701'
        AND accession.accession_date <= '20160631'
