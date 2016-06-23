SELECT 
    accession.identifier,
    accession.title,
    accession_date,
    extent.number as 'extent_number',
    enumeration_value.value AS 'extent_unit',
    extent.container_summary,
    accession.content_description,
    accession.access_restrictions_note,
    accession.use_restrictions_note,
    accession.acquisition_type_id,
    accession.created_by
FROM
    accession
        LEFT JOIN
    extent on accession.id = extent.accession_id
        LEFT JOIN
    enumeration_value ON extent.extent_type_id = enumeration_value.id
WHERE
    accession.accession_date >= '20150701'
        AND accession.accession_date <= '20160631'
        AND repo_id = 2
