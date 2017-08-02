**accessions_acquired_FYreport_final.sql** - SQL script that queries ASpace SQL database for information about accessions acquired in a given time period (typically a fiscal year).

**accessions_without_acquisition_type.sql** - SQL script that queries ASpace SQL database for list of accessions missing an acquisition type value. Used for periodic data QC.

**accessions_without_extent.sql** - SQL script that queries ASpace SQL database for list of accessions missing an extent statement of any kind. Used for periodic data QC.

**accessions_without_extent_in_linear_feet.sql** - SQL script that queries ASpace SQL database for list of accessions missing an extent statement in linear feet. Used for periodic data QC.

**accessions_without_extent_number.sql** - SQL script that queries ASpace SQL database for list of accessions missing an extent number. Used for periodic data QC.

**extent_accessioned_by_acquisition_type.sql** - SQL script that queries ASpace SQL database and generates a report showing extent (number and linear_feet) of accessions by acqusition type (gift, purchase, etc.).

**extent_accessioned_by_research_center.sql** - SQL script that queries ASpace SQL database and generates a report showing extent (number and linear_feet) of accessions by Rubenstein Library research center (Hartman, Bingham, Franklin, etc.)

**accession_resource_relationship.sql** - SQL script that queries ASpace database and pulls selected fields for all accession records, including any linked resource records IDs and titles.
