<xsl:stylesheet version="2.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xmlns:ead="urn:isbn:1-931666-22-9"
    xmlns:ns2="stoopid fake namespace"
    xmlns="urn:isbn:1-931666-22-9" 
    exclude-result-prefixes="ead xsi xs">
    
    <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
    
    <!--Identity template to copy entire EAD source document -->
    <xsl:template match="@*|node()" name="identity">
        <!-- identity transform is default -->
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>

<!-- Most issues fixed below are identified when batch-validating bulk EAD exports from ASpace -->
	
	
    <xsl:template match="@href[parent::ead:extref]|@href[parent::ead:archref]|@href[parent::ead:ref]|@href[parent::ead:bibref]">
        <xsl:attribute name="xlink:href">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>
    
    <xsl:template match="@title[parent::ead:extref]|@title[parent::ead:archref]|@title[parent::ead:ref]|@title[parent::ead:bibref]">
        <xsl:attribute name="xlink:title">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>
    
    <xsl:template match="@linktype[parent::ead:extref]|@linktype[parent::ead:archref]|@linktype[parent::ead:ref]|@linktype[parent::ead:bibref]">
        <xsl:attribute name="xlink:type">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>
    
    <xsl:template match="@show[parent::ead:extref]|@show[parent::ead:archref]|@show[parent::ead:ref]|@show[parent::ead:bibref]">
        <xsl:attribute name="xlink:show">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>
    
    <xsl:template match="@actuate[parent::ead:extref]|@actuate[parent::ead:archref]|@actuate[parent::ead:ref]|@actuate[parent::ead:bibref]">
        <xsl:attribute name="xlink:actuate">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>
    
    <!-- Does this work to remove attribute altogether? -->
    <xsl:template match="@type[parent::ead:extref]|@type[parent::ead:archref]|@type[parent::ead:ref]|@type[parent::ead:bibref]"/>
     
     <xsl:template match="@target[parent::ead:ref]"/>
     
     
<!--Eliminate <ref> elements within scopecontent/p -->
<xsl:template match="//ead:scopecontent/ead:p/ead:ref">
    <xsl:value-of select="normalize-space(.)"/>
</xsl:template>    
  

<!-- fix source='center name' -->
    <xsl:template match="@source[.='center name']">
        <xsl:attribute name="source">
            <xsl:text>local</xsl:text>
        </xsl:attribute>
    </xsl:template>
    
    
<!--Remove <dao> when xlink:href contains [path] -->
    <xsl:template match="ead:dao[@xlink:href='[path]']"/>
    
<!-- DOES THIS WORK? Remove empty note (without <p> subnote) -->
    <xsl:template match="//ead:scopecontent[not(ead:p)]"/>
    <xsl:template match="//ead:odd[not(ead:p)]"/>
    <xsl:template match="//ead:arrangement[not(ead:p)]"/>
    <xsl:template match="//ead:accessrestrict[not(ead:p)]"/>
    
<!-- Fixes occurences of "Missing Title" supplied in AT-AS migration for all bioghist/chronlist/head elements -->
    <xsl:template match="//ead:chronlist/ead:head">
        <xsl:choose>
           <xsl:when test="contains(.,'Missing Title')">
                <xsl:element name="head">Chronology</xsl:element>
           </xsl:when>
           <xsl:otherwise>
               <xsl:element name="head">
                   <xsl:apply-templates/>
               </xsl:element>
           </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
       
    
</xsl:stylesheet>