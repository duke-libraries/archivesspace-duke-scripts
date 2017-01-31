<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:ead="urn:isbn:1-931666-22-9" 
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns="urn:isbn:1-931666-22-9" exclude-result-prefixes="ead">


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

    <xsl:template name="replace-string">
        <xsl:param name="text"/>
        <xsl:param name="replace"/>
        <xsl:param name="with"/>
        <xsl:choose>
            <xsl:when test="contains($text,$replace)">
                <xsl:value-of select="substring-before($text,$replace)"/>
                <xsl:value-of select="$with"/>
                <xsl:call-template name="replace-string">
                    <xsl:with-param name="text"
                        select="substring-after($text,$replace)"/>
                    <xsl:with-param name="replace" select="$replace"/>
                    <xsl:with-param name="with" select="$with"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$text"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>



    <xsl:template match="/">

        <!-- Column Headers -->

        <xsl:text>Container_1</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>Container_2</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>Container_3</xsl:text>
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
        
        <xsl:text>Subseries_title</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>Date_normal</xsl:text>
        <xsl:value-of select="$tab"/>

<!-- DON'T NEET THESE
        <xsl:text>Scopecontent</xsl:text>
        <xsl:value-of select="$tab"/>
        -->

        <!-- Infrequent, remove comment if needed
        <xsl:text>Provenance</xsl:text>
        <xsl:value-of select="$tab"/>
-->

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

        <!-- might need to manipulate resulting sheet if collection contains both file and item-level components -->
        <xsl:for-each select="//ead:*[@level = 'file']|//ead:*[@level = 'item']">

            <!-- First container, e.g. Box -->
            <xsl:value-of select="ead:did/ead:container[1]"/>
            <xsl:value-of select="$tab"/>

            <!-- Second container, e.g. Folder -->

            <xsl:value-of select="normalize-space(ead:did/ead:container[2])"/>
            <xsl:value-of select="$tab"/>
            
            <xsl:value-of select="normalize-space(ead:did/ead:container[3])"/>
            <xsl:value-of select="$tab"/>


            <!-- Folder/file/item title -->
            <xsl:value-of select="normalize-space(ead:did/ead:unittitle)"/>
            <xsl:value-of select="$tab"/>

            <!-- Date Expression -->

            <xsl:value-of select="ead:did/ead:unitdate"/>
            <xsl:value-of select="$tab"/>


            <!-- controlled extent statement, typically # of items or pages -->
            <xsl:value-of select="normalize-space(ead:did/ead:physdesc/ead:extent[1])"/>
            <xsl:value-of select="$tab"/>


            <!-- any other kind of physical description if present -->
            <xsl:value-of select="normalize-space(ead:did/ead:physdesc[not(ead:extent)])"/>
            <xsl:value-of select="$tab"/>

            <!-- Placeholder column, values to be supplied in spreadsheet after digitization -->
            <xsl:text>[DIGITAL OBJECT ID]</xsl:text>
            <xsl:value-of select="$tab"/>

            <!-- Series Title -->
            <xsl:value-of select="normalize-space(ancestor::ead:*[@level = 'series'][1]/ead:did/ead:unittitle)"/>
            <xsl:value-of select="$tab"/>

            <!-- Subseries Title -->
            <xsl:value-of select="normalize-space(ancestor::ead:*[@level = 'subseries'][1]/ead:did/ead:unittitle)"/>
            <xsl:value-of select="$tab"/>

            <!-- Normalized Date -->
            <xsl:value-of select="ead:did/ead:unitdate/@normal"/>
            <xsl:value-of select="$tab"/>

            <!-- Scopecontent notes, probably don't need these
            <xsl:value-of select="normalize-space(ead:scopecontent[1]/ead:p)"/>
            <xsl:value-of select="$tab"/> -->

            <!-- Item-level provenance info.  Infrequent, remove comment if neede
            <xsl:value-of select="normalize-space(ead:acqinfo/ead:p)"/>
            <xsl:value-of select="$tab"/>
            -->

<!-- Get all the subject, name, and place name headings and separate with semicolons
 
Infrequent, remove comment if needed
 
    <xsl:if test="ead:controlaccess/ead:subject"><xsl:for-each select="ead:controlaccess/ead:subject"><xsl:value-of select="normalize-space(.)"/><xsl:choose><xsl:when test="position()=last()"/><xsl:otherwise><xsl:text>; </xsl:text></xsl:otherwise></xsl:choose></xsl:for-each></xsl:if><xsl:value-of select="$tab"/>

    <xsl:if test="ead:controlaccess/ead:persname|ead:controlaccess/ead:corpname|ead:controlaccess/ead:famname"><xsl:for-each select="ead:controlaccess/ead:persname|ead:controlaccess/ead:corpname|ead:controlaccess/ead:famname"><xsl:value-of select="normalize-space(.)"/><xsl:choose><xsl:when test="position()=last()"/><xsl:otherwise><xsl:text>; </xsl:text></xsl:otherwise></xsl:choose></xsl:for-each></xsl:if><xsl:value-of select="$tab"/>

    <xsl:if test="ead:controlaccess/ead:geogname"><xsl:for-each select="ead:controlaccess/ead:geogname"><xsl:value-of select="normalize-space(.)"/><xsl:choose><xsl:when test="position()=last()"/><xsl:otherwise><xsl:text>; </xsl:text></xsl:otherwise></xsl:choose></xsl:for-each></xsl:if><xsl:value-of select="$tab"/>
  -->

            <!-- ASpace refID for Archival Object record, strip "aspace_" prefix from these values-->
            <!-- Terribly cumbersome XSLT 1.0 string replace (template at top) -->
            <xsl:call-template name="replace-string">
                <xsl:with-param name="text" select="./@id"/>
                <xsl:with-param name="replace" select="'aspace_'" />
                <xsl:with-param name="with" select="''"/>
            </xsl:call-template>
            
            <!-- XSLT 2.0 simple string replace
            <xsl:value-of select="replace(normalize-space(./@id),'aspace_','')"/> -->
            
            <xsl:value-of select="$tab"/>
            <!-- Placeholder column, values to be supplied in spreadsheet after digitization -->
            <!--<xsl:text>[DIGITAL OBJECT URI]</xsl:text>-->
            <xsl:value-of select="ead:did/ead:dao/@xlink:href"/>
            <xsl:value-of select="$tab"/>

            <xsl:value-of select="$newline"/>

        </xsl:for-each>

    </xsl:template>

</xsl:stylesheet>
