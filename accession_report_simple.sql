select identifier, title, accession_date, extent.number, enumeration_value.value, extent.extent_type_id, extent.container_summary, content_description, access_restrictions
from accession
left join extent on accession.id = extent.accession_id
left join enumeration_value on extent_type_id = enumeration_value.id
where accession.accession_date >= '20150701' #change dates as needed
and accession.accession_date <= '20160317'