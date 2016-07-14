SELECT 
    ev1.value AS 'processing_status',
    COUNT(accession.id) AS '# of accessions'
FROM
    accession
        LEFT JOIN
    collection_management ON accession.id = collection_management.accession_id
        LEFT JOIN
    enumeration_value ev1 ON collection_management.processing_status_id = ev1.id
WHERE
    repo_id = 2
        AND accession.accession_date >= '20150701'
        AND accession.accession_date <= '20160631'
GROUP BY ev1.value;
