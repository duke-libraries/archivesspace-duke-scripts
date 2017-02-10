<xsl:stylesheet version="2.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:ead="urn:isbn:1-931666-22-9" 
    xmlns="urn:isbn:1-931666-22-9" 
    exclude-result-prefixes="ead">


    <!-- This XSLT is used to transform EAD exported from ArchivesSpace into the basis of a digitization guide spreadsheet (TSV)
for use by the DPC.  The stylesheet can be modified to extract either item or file-level component metadata.
Some columns may be removed (commented out) based on metadata availble for any given component.
This XSLT will supply placeholder columns for the DPC ID and the URI for the digitized item.
Values should be added to these columns during hte digitization process or after digitization.
Once the digitiztaion guide spreadsheet is complete it can be used as for ingest into the Duke Digital Repository or CONTENTdm.
The completed digitization guide can also be used to create Digital Object Records in ASpace and link them to the appropriate Archival Object record.
To do so, use this digitization guide as the imput file for the duke_update_archival_object.py script.
-->

    <xsl:output method="text" encoding="UTF-8"/>

    <xsl:strip-space elements="*"/>

    <xsl:variable name="tab">
        <xsl:text>&#x09;</xsl:text>
    </xsl:variable>

    <xsl:variable name="newline">
        <xsl:text>&#xa;</xsl:text>
    </xsl:variable>

    <xsl:template match="/">

        <!-- Column Headers -->

        <xsl:text>Creator/Contributor</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>Container_1</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>Container_2</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>Title</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>Date</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>Extent</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>Physdesc</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>DPC_ID</xsl:text>
        <!-- Empty column, to be supplied by DPC after digitization -->
        <xsl:value-of select="$tab"/>

        <xsl:text>Series_title</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>Date_normal</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>Description</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>isPartOf</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>Rights</xsl:text>
        <xsl:value-of select="$tab"/>

        <!-- Infrequent, remove comment if needed -->
        <xsl:text>Provenance</xsl:text>
        <xsl:value-of select="$tab"/>

        <!--Infrequent at component level, remove comment if needed
       
    <xsl:text>Subject-Topical</xsl:text>
    <xsl:value-of select="$tab"/>
  
    <xsl:text>Subject-Name</xsl:text>
    <xsl:value-of select="$tab"/>
 
    <xsl:text>Subject-Geographic</xsl:text>
    <xsl:value-of select="$tab"/>
    
-->

        <xsl:text>ASpace_componentID</xsl:text>
        <xsl:value-of select="$tab"/>

        <!-- Empty column, to be supplied after URI is established, ARKs? -->
        <xsl:text>Digital_Object_URI</xsl:text>
  




        <!-- Begin Data Rows -->
        <xsl:value-of select="$newline"/>

        <!-- only process file and item level components that container <dao> tags -->
        <xsl:for-each select="//ead:*[@level = 'item'][ead:did/ead:dao]|//ead:*[@level='file'][ead:did/ead:dao]">

            <!--Creator/Contributor from origination -->
            <xsl:value-of select="normalize-space(ancestor::*//ead:origination)"/>
            <xsl:value-of select="$tab"/>
            
            <!-- First container, e.g. Box -->
            <xsl:value-of select="translate(ead:did/ead:container[1]/@type,'bf','BF')"/>
            <xsl:text> </xsl:text>
            <xsl:value-of select="ead:did/ead:container[1]"/>
            <xsl:value-of select="$tab"/>

            <!-- Second container, e.g. Folder -->

            <xsl:value-of select="translate(ead:did/ead:container[2]/@type,'fp','FP')"/>
            <xsl:text> </xsl:text>
            <xsl:value-of select="ead:did/ead:container[2]"/>
            <xsl:value-of select="$tab"/>


            <!-- Folder/file/item title -->
            <xsl:value-of select="normalize-space(./ead:did/ead:unittitle)"/>
            <xsl:value-of select="$tab"/>

            <!-- Date Expression -->

            <xsl:value-of select="normalize-space(ead:did/ead:unitdate)"/>
            <xsl:value-of select="$tab"/>


            <!-- controlled extent statement, typically # of items or pages -->
            <xsl:value-of select="normalize-space(ead:did/ead:physdesc/ead:extent[1])"/>
            <xsl:value-of select="$tab"/>


            <!-- any other kind of physical description if present -->
            <xsl:value-of select="normalize-space(ead:did/ead:physdesc[not(ead:extent)])"/>
            <xsl:value-of select="$tab"/>
   
            <!-- only DPCID form URI -->
            <xsl:value-of select="replace(ead:did/ead:dao/@xlink:href,'.*/(.*)/$','$1')"/>
            
            <xsl:value-of select="$tab"/>

            <!-- Series Title -->
            <xsl:value-of select="normalize-space(ancestor::ead:*[@level = 'series']/ead:did/ead:unittitle)"/>
            <xsl:value-of select="$tab"/>

            <!-- Normalized Date -->
            <xsl:value-of select="ead:did/ead:unitdate/@normal"/>
            <xsl:value-of select="$tab"/>

            <!-- Scopecontent notes, probably don't need these -->
            <xsl:value-of select="normalize-space(ead:scopecontent[1]/ead:p[1])"/>
            <xsl:value-of select="$tab"/>
            
            <!-- isPartof from EADID -->
            <xsl:value-of select="ancestor::*//ead:eadid"/>
            <xsl:value-of select="$tab"/>
            
            <!-- Rights -->
            <xsl:for-each select="ancestor::*//ead:archdesc/ead:userestrict/ead:p">
            <xsl:value-of select="normalize-space(.)"/><xsl:text> </xsl:text>
            </xsl:for-each>
            <xsl:value-of select="$tab"/>

            <!-- Collection-level provenance info. -->
            <xsl:for-each select="ancestor::*//ead:archdesc/ead:acqinfo/ead:p">
                <xsl:value-of select="normalize-space(.)"/><xsl:text> </xsl:text>
            </xsl:for-each>
            <xsl:value-of select="$tab"/>


<!-- Get all the subject, name, and place name headings and separate with semicolons
 
Infrequent, remove comment if needed
 
    <xsl:if test="ead:controlaccess/ead:subject"><xsl:for-each select="ead:controlaccess/ead:subject"><xsl:value-of select="normalize-space(.)"/><xsl:choose><xsl:when test="position()=last()"/><xsl:otherwise><xsl:text>; </xsl:text></xsl:otherwise></xsl:choose></xsl:for-each></xsl:if><xsl:value-of select="$tab"/>

    <xsl:if test="ead:controlaccess/ead:persname|ead:controlaccess/ead:corpname|ead:controlaccess/ead:famname"><xsl:for-each select="ead:controlaccess/ead:persname|ead:controlaccess/ead:corpname|ead:controlaccess/ead:famname"><xsl:value-of select="normalize-space(.)"/><xsl:choose><xsl:when test="position()=last()"/><xsl:otherwise><xsl:text>; </xsl:text></xsl:otherwise></xsl:choose></xsl:for-each></xsl:if><xsl:value-of select="$tab"/>

    <xsl:if test="ead:controlaccess/ead:geogname"><xsl:for-each select="ead:controlaccess/ead:geogname"><xsl:value-of select="normalize-space(.)"/><xsl:choose><xsl:when test="position()=last()"/><xsl:otherwise><xsl:text>; </xsl:text></xsl:otherwise></xsl:choose></xsl:for-each></xsl:if><xsl:value-of select="$tab"/>
  -->

            <!-- ASpace refID for Archival Object record, strips the "aspace_" prefix from these values-->
             <xsl:value-of select="replace(normalize-space(./@id),'aspace_','')"/>
            <xsl:value-of select="$tab"/>

            <!-- Placeholder column, values to be supplied in spreadsheet after digitization -->
            <!-- <xsl:text>[DIGITAL OBJECT URI]</xsl:text>-->
            
            <!-- Full URI -->
            <xsl:value-of select="ead:did/ead:dao/@xlink:href"/>
           

            <xsl:value-of select="$newline"/>

        </xsl:for-each>

    </xsl:template>

</xsl:stylesheet>
