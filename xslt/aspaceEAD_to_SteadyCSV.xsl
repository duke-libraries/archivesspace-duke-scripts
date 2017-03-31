<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:ead="urn:isbn:1-931666-22-9" 
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns="urn:isbn:1-931666-22-9" exclude-result-prefixes="ead">


    <!-- This XSLT is used to transform EAD exported from ArchivesSpace into a TSV.
The TSV can be opened and edited in Excel or Google Sheets, saved as a CSV.
CSV can be submitted to Steady service to convert to EAD, suitable for import into ASpace.
Allows a rudimentary form of EAD to Excel to EAD roundtripping in ASpace.
Use with caution.
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

        <xsl:text>instance type</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>container 1 type</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>container 1 number</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>container 2 type</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>container 2 number</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>container 3 type</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>container 3 number</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>series number</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>series title</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>series dates</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>subseries number</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>subseries title</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>subseries dates</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>c0x_level(ignored)</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>file id</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>file title</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>file dates</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>file-date-normal</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>physdesc</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>extent</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>conditions governing access</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>scopecontent</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>note1</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>note2</xsl:text>
        <xsl:value-of select="$tab"/>

        <xsl:text>DAO</xsl:text>
        <xsl:value-of select="$tab"/>
        
        <xsl:text>ASpace_refID</xsl:text>
        
<!-- ################################################################## -->        
        
        <!-- Begin Data Rows -->
        <xsl:value-of select="$newline"/>

        <!-- might need to manipulate resulting sheet if collection contains both file and item-level components -->
        <xsl:for-each select="//ead:*[@level = 'file']|//ead:*[@level = 'item']">

            <!-- Hardcode mixed_materials -->
            <xsl:text>mixed_materials</xsl:text>    
            <xsl:value-of select="$tab"/>
            
            <!-- First container type, e.g. Box -->
            <xsl:value-of select="ead:did/ead:container[1]/@type"/>
            <xsl:value-of select="$tab"/>
            
            <!-- First container number -->
            <xsl:value-of select="ead:did/ead:container[1]"/>
            <xsl:value-of select="$tab"/>

            <xsl:value-of select="ead:did/ead:container[2]/@type"/>
            <xsl:value-of select="$tab"/>
            
            <!-- Second container, e.g. Folder -->
            <xsl:value-of select="normalize-space(ead:did/ead:container[2])"/>
            <xsl:value-of select="$tab"/>
            
            <xsl:value-of select="ead:did/ead:container[3]/@type"/>
            <xsl:value-of select="$tab"/>
            
            <xsl:value-of select="normalize-space(ead:did/ead:container[3])"/>
            <xsl:value-of select="$tab"/>

            <!-- Series Number if present in unitid (typically not) -->
            <xsl:value-of select="normalize-space(ancestor::ead:*[@level = 'series'][1]/ead:did/ead:unitid)"/>
            <xsl:value-of select="$tab"/>

            <!-- Series Title -->
            <xsl:value-of select="normalize-space(ancestor::ead:*[@level = 'series'][1]/ead:did/ead:unittitle)"/>
            <xsl:value-of select="$tab"/>

            <!-- Series date expression-->
            <xsl:value-of select="normalize-space(ancestor::ead:*[@level = 'series'][1]/ead:did/ead:unitdate)"/>
            <xsl:value-of select="$tab"/>

            <!-- Subseries number -->
            <xsl:value-of select="normalize-space(ancestor::ead:*[@level = 'subseries'][1]/ead:did/ead:unitid)"/>
            <xsl:value-of select="$tab"/>
            
            <!-- Subseries Title -->
            <xsl:value-of select="normalize-space(ancestor::ead:*[@level = 'subseries'][1]/ead:did/ead:unittitle)"/>
            <xsl:value-of select="$tab"/>

            <!-- Subseries dates -->
            <xsl:value-of select="normalize-space(ancestor::ead:*[@level = 'subseries'][1]/ead:did/ead:unitdate)"/>
            <xsl:value-of select="$tab"/>


            <!-- c0x level  -->
            <xsl:value-of select="local-name()"/>
            <xsl:value-of select="$tab"/>
            
            <!-- file or item title -->
            <xsl:value-of select="normalize-space(ead:did/ead:unitid)"/>
            <xsl:value-of select="$tab"/>

            <!-- file or item title -->
            <xsl:value-of select="normalize-space(ead:did/ead:unittitle)"/>
            <xsl:value-of select="$tab"/>

            <!-- file Date Expression -->
            <xsl:value-of select="normalize-space(ead:did/ead:unitdate)"/>
            <xsl:value-of select="$tab"/>

            <!-- file date normalized -->
            <xsl:value-of select="ead:did/ead:unitdate/@normal"/>
            <xsl:value-of select="$tab"/>

            <!-- any other kind of physical description if present -->
            <xsl:value-of select="normalize-space(ead:did/ead:physdesc[not(ead:extent)])"/>
            <xsl:value-of select="$tab"/>

            <!-- controlled extent statement, typically # of items or pages -->
            <xsl:value-of select="normalize-space(ead:did/ead:physdesc/ead:extent[1])"/>
            <xsl:value-of select="$tab"/>

            <!-- Access restriction note -->
            <xsl:for-each select="ead:accessrestrict/ead:p">
                <xsl:value-of select="normalize-space(.)"/>
                <xsl:if test="not(position() = last())"><xsl:text> </xsl:text></xsl:if>
            </xsl:for-each>
            <xsl:value-of select="$tab"/>

            <!-- Scopecontent notes, comment out if you don't need these -->
            <xsl:for-each select="ead:scopecontent/ead:p">
                <xsl:value-of select="normalize-space(.)"/>
                <xsl:if test="not(position() = last())"><xsl:text> </xsl:text></xsl:if>
            </xsl:for-each>
            <xsl:value-of select="$tab"/>
            
            <!-- Note1 -->
            <xsl:text></xsl:text>
            <xsl:value-of select="$tab"/>
            
            <!-- Note2 -->
            <xsl:text></xsl:text>
            <xsl:value-of select="$tab"/>
            
                       
            <!-- DAOs -->
            <xsl:value-of select="ead:did/ead:dao/@xlink:href"/>
            <xsl:value-of select="$tab"/>
            
            <!-- ASpace refID for Archival Object record, strip "aspace_" prefix from these values-->
            <xsl:value-of select="replace(normalize-space(./@id),'aspace_','')"/>
            
            
<!-- Get all the subject, name, and place name headings and separate with semicolons
 
Infrequent, remove comment if needed
 
    <xsl:if test="ead:controlaccess/ead:subject"><xsl:for-each select="ead:controlaccess/ead:subject"><xsl:value-of select="normalize-space(.)"/><xsl:choose><xsl:when test="position()=last()"/><xsl:otherwise><xsl:text>; </xsl:text></xsl:otherwise></xsl:choose></xsl:for-each></xsl:if><xsl:value-of select="$tab"/>

    <xsl:if test="ead:controlaccess/ead:persname|ead:controlaccess/ead:corpname|ead:controlaccess/ead:famname"><xsl:for-each select="ead:controlaccess/ead:persname|ead:controlaccess/ead:corpname|ead:controlaccess/ead:famname"><xsl:value-of select="normalize-space(.)"/><xsl:choose><xsl:when test="position()=last()"/><xsl:otherwise><xsl:text>; </xsl:text></xsl:otherwise></xsl:choose></xsl:for-each></xsl:if><xsl:value-of select="$tab"/>

    <xsl:if test="ead:controlaccess/ead:geogname"><xsl:for-each select="ead:controlaccess/ead:geogname"><xsl:value-of select="normalize-space(.)"/><xsl:choose><xsl:when test="position()=last()"/><xsl:otherwise><xsl:text>; </xsl:text></xsl:otherwise></xsl:choose></xsl:for-each></xsl:if><xsl:value-of select="$tab"/>
  -->

            <xsl:value-of select="$newline"/>

        </xsl:for-each>

    </xsl:template>

</xsl:stylesheet>
