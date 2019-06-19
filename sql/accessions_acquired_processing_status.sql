/* Will only report accession counts for those accessions that have extent recorded in linear feet
need to run QC scripts first to find accessions without lf count */
SELECT
    ev1.value AS 'processing_status',
    COUNT(accession.id) AS '# of accessions',
    ROUND(SUM(extent.number), 2) AS 'total_extent_lf'
FROM
    accession
        LEFT JOIN
    collection_management ON accession.id = collection_management.accession_id
        LEFT JOIN
    enumeration_value ev1 ON collection_management.processing_status_id = ev1.id
        LEFT JOIN
    extent on accession.id = extent.accession_id
        LEFT JOIN
    enumeration_value ev2 ON extent.extent_type_id = ev2.id
WHERE
    repo_id = 2
        AND accession.accession_date >= '20180701'
        AND accession.accession_date <= '20190631'
        AND ev2.value LIKE '%linear%'
GROUP BY
    ev1.value WITH ROLLUP
