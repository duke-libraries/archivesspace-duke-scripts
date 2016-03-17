select value as 'Accession type', COUNT(*) as 'Total accessions measured in linear feet', ROUND(SUM(extent.number), 2) as 'Linear feet'
from accession
left join extent on accession.id = extent.accession_id
left join enumeration_value on acquisition_type_id = enumeration_value.id 
where (extent_type_id IN (select id from enumeration_value
where LOWER(value) like '%linear%'))
and repo_id = 2 #hardcoded value for now
and accession.accession_date >= '20151001' #change dates as needed
and accession.accession_date <= '20151231'
group by acquisition_type_id;