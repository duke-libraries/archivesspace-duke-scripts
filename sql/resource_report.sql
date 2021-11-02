SELECT
    resource.id as 'aspace_resource_id',
    replace(replace(replace(replace(replace(resource.identifier, ',', '.'), '"', ''), ']', ''), '[', ''), '.null', '') as collection_id,
    resource.title,
    extent.number as 'extent_number',
    ev1.value AS 'extent_type',
    extent.container_summary,
    resource.ead_id,
    resource.ead_location as 'finding_aid_url',
    resource.finding_aid_note,
    resource.repository_processing_note,
    resource.finding_aid_date,
    resource.finding_aid_author,
    resource.created_by,
    resource.last_modified_by,
    resource.system_mtime,
    GROUP_CONCAT(accession.id) as 'related_accessions_aspace_ids',
    GROUP_CONCAT(accession.identifier) as 'related_accessions_identifiers',
    GROUP_CONCAT(accession.title) as 'related_accessions_titles'
FROM
    resource
        LEFT JOIN
    extent on resource.id = extent.resource_id
        LEFT JOIN
    spawned_rlshp ON resource.id = spawned_rlshp.resource_id
        LEFT JOIN
    accession ON spawned_rlshp.accession_id = accession.id
        LEFT JOIN
    enumeration_value ev1 ON extent.extent_type_id = ev1.id
WHERE
    resource.repo_id = 2 AND resource.identifier LIKE '%UA%'
GROUP BY resource.id
ORDER BY
    resource.identifier;
