<?xml version='1.0'?>
<xsl:stylesheet version="2.0" 
				xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
				xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
				xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
				xmlns:bf="http://id.loc.gov/ontologies/bibframe/"
				xmlns:dct="http://purl.org/dc/terms/"
				xmlns:htrc="http://wcsa.htrc.illinois.edu/">

<!--	<xsl:ourput encoding="UTF-8" method="text" />
	<xsl:strip-space elements="*"/>-->

	<xsl:template match='/'>
<!--		<xsl:variable name="saveAs" select="ef_example.jsonld"/>-->

		<xsl:result-document href="ef_example4.jsonld" method='text' exclude-result-prefixes="#all" omit-xml-declaration="yes" indent="no" encoding="UTF-8">
				<xsl:text>{ &#10;	"@context": [</xsl:text>
				<xsl:text> &#10;		"http://schema.org"</xsl:text>
				<xsl:text>, &#10;		{</xsl:text>
				<xsl:text> &#10;			"htrc": "http://wcsa.htrc.illinois.edu/"</xsl:text>
				<xsl:text>, &#10;			"accessProfile": {</xsl:text>
				<xsl:text> &#10;				"@id": "htrc:accessProfile"</xsl:text>
				<xsl:text> &#10;			}</xsl:text>
				<xsl:text>, &#10;			"title": "name"</xsl:text>
				<xsl:text>, &#10;			"enumerationChronology": {</xsl:text>
				<xsl:text> &#10;				"@id": "htrc:enumerationChronology"</xsl:text>
				<xsl:text> &#10;			}</xsl:text>
				<xsl:text>, &#10;			"pubDate": "datePublished"</xsl:text>
				<xsl:text>, &#10;			"pubPlace": "locationCreated"</xsl:text>
				<xsl:text>, &#10;			"language": "inLanguage"</xsl:text>
				<xsl:text>, &#10;			"rightsAttributes": {</xsl:text>
				<xsl:text> &#10;				"@id": "htrc:accessRights"</xsl:text>
				<xsl:text> &#10;			}</xsl:text>
				<xsl:text>, &#10;			"contributor": {</xsl:text>
				<xsl:text> &#10;				"@id": "schema:contributor"</xsl:text>
				<xsl:text>, &#10;				"@container": "@list"</xsl:text>
				<xsl:text> &#10;			}</xsl:text>
				<xsl:text>, &#10;			"sourceInstitution": "provider"</xsl:text>
				<xsl:text>, &#10;			"lastUpdateDate": "dateModified"</xsl:text>
				<xsl:text>, &#10;			"identifier": {</xsl:text>
				<xsl:text> &#10;				"@id": "schema:identifier"</xsl:text>
				<xsl:text>, &#10;				"@container": "@list"</xsl:text>
				<xsl:text> &#10;			}</xsl:text>
				<xsl:text> &#10;		}</xsl:text>
				<xsl:text> &#10;	]</xsl:text>
				<xsl:text>, &#10;	"type": "Dataset"</xsl:text>
				<xsl:text>, &#10;	"schemaVersion": "https://wiki.htrc.illinois.edu/display/COM/Extracted+Features+Dataset_2.0"</xsl:text>
				<xsl:text>, &#10;	"sourceInstitution": "htrc"</xsl:text>
				<xsl:text>, &#10;	"about": {</xsl:text>
				<xsl:text> &#10;		"id": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Item/@rdf:about" /><xsl:text>"</xsl:text>
				<xsl:text>, &#10;		"type": "</xsl:text><xsl:value-of select="substring(/rdf:RDF/bf:Work/rdf:type/@rdf:resource,39)" /><xsl:text>"</xsl:text>
				<xsl:text>, &#10;		"isAccessibleForFree": "</xsl:text>
					<xsl:choose>
						<xsl:when test="/rdf:RDF/bf:Item/dct:accessRights/text() = 'pd'">
							<xsl:text>TRUE</xsl:text>
						</xsl:when>
						<xsl:otherwise>
							<xsl:text>FALSE</xsl:text>
						</xsl:otherwise>
					</xsl:choose>
				<xsl:text>"</xsl:text>
				<xsl:text>, &#10;		"title": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Work/bf:title/bf:Title/rdfs:label/text()" /><xsl:text>"</xsl:text>
				<xsl:call-template name="contribution_agents">
					<xsl:with-param name="node" select="/rdf:RDF/bf:Work/bf:contribution/bf:Contribution" />
				</xsl:call-template>
				<xsl:if test="/rdf:RDF/bf:Instance/bf:provisionActivity/bf:ProvisionActivity/bf:agent/bf:Agent/rdfs:label">
					<xsl:text>, &#10;		"publisher": {</xsl:text>
					<xsl:text> &#10;			"type": "Organization"</xsl:text>
					<xsl:text>, &#10;			"name": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Instance/bf:provisionActivity/bf:ProvisionActivity/bf:agent/bf:Agent/rdfs:label/text()" /><xsl:text>"</xsl:text>
					<xsl:text> &#10;		}</xsl:text>
				</xsl:if>
				<xsl:choose>
					<xsl:when test="/rdf:RDF/bf:Instance/bf:provisionActivity/bf:ProvisionActivity/bf:place/bf:Place/@rdf:about and /rdf:RDF/bf:Instance/bf:provisionActivity/bf:ProvisionActivity/bf:place/bf:Place/rdfs:label">
						<xsl:text>, &#10;		"pubPlace": [</xsl:text>
						<xsl:text> &#10;			"</xsl:text><xsl:value-of select="/rdf:RDF/bf:Instance/bf:provisionActivity/bf:ProvisionActivity/bf:place/bf:Place/@rdf:about" /><xsl:text>"</xsl:text>
						<xsl:text>, &#10;			"</xsl:text><xsl:value-of select="/rdf:RDF/bf:Instance/bf:provisionActivity/bf:ProvisionActivity/bf:place/bf:Place/rdfs:label/text()" /><xsl:text>"</xsl:text>
						<xsl:text> &#10;		]</xsl:text>
					</xsl:when>
					<xsl:otherwise>
						<xsl:choose>
							<xsl:when test="/rdf:RDF/bf:Instance/bf:provisionActivity/bf:ProvisionActivity/bf:place/bf:Place/@rdf:about">
								<xsl:text>, &#10;		"pubPlace": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Instance/bf:provisionActivity/bf:ProvisionActivity/bf:place/bf:Place/@rdf:about" /><xsl:text>"</xsl:text>
							</xsl:when>
							<xsl:otherwise>
								<xsl:if test="/rdf:RDF/bf:Instance/bf:provisionActivity/bf:ProvisionActivity/bf:place/bf:Place/rdfs:label">
									<xsl:text>, &#10;		"pubPlace": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Instance/bf:provisionActivity/bf:ProvisionActivity/bf:place/bf:Place/rdfs:label/text()" /><xsl:text>"</xsl:text>
								</xsl:if>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:otherwise>
				</xsl:choose>
				<xsl:choose>
					<xsl:when test="/rdf:RDF/bf:Work/bf:language/bf:Language/bf:identifiedBy/bf:Identifier/rdf:value/@rdf:resource">
						<xsl:choose>
							<xsl:when test="count(/rdf:RDF/bf:Work/bf:language/bf:Language/bf:identifiedBy/bf:Identifier/rdf:value/@rdf:resource) > 1">
								<xsl:text>, &#10;		"language": [</xsl:text>
								<xsl:for-each select="/rdf:RDF/bf:Work/bf:language/bf:Language/bf:identifiedBy/bf:Identifier/rdf:value/@rdf:resource">
									<xsl:text> &#10;			"</xsl:text><xsl:value-of select="substring(.,40)" /><xsl:text>"</xsl:text>
									<xsl:if test="position() != last()">
										<xsl:text>, </xsl:text>
									</xsl:if>
								</xsl:for-each>
								<xsl:text> &#10;		]</xsl:text>
							</xsl:when>
							<xsl:otherwise>
								<xsl:text>, &#10;		"language": "</xsl:text><xsl:value-of select="substring(/rdf:RDF/bf:Work/bf:language/bf:Language/bf:identifiedBy/bf:Identifier/rdf:value/@rdf:resource,40)" /><xsl:text>"</xsl:text>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:when>
					<xsl:otherwise>
						<xsl:if test="/rdf:RDF/bf:Work/bf:language/bf:Language/@rdf:about">
							<xsl:text>, &#10;		"language": "</xsl:text><xsl:value-of select="substring(/rdf:RDF/bf:Work/bf:language/bf:Language/@rdf:about,40)" /><xsl:text>"</xsl:text>
						</xsl:if>
					</xsl:otherwise>
				</xsl:choose>
				<xsl:if test="/rdf:RDF/bf:Item/dct:accessRights">
					<xsl:text>, &#10;		"rightsAttributes": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Item/dct:accessRights/text()" /><xsl:text>"</xsl:text>
				</xsl:if>
				<xsl:if test="/rdf:RDF/bf:Item/htrc:contentProviderAgent/@rdf:resource">
					<xsl:text>, &#10;		"sourceInstitution": {</xsl:text>
					<xsl:text> &#10;			"name": "</xsl:text><xsl:value-of select="substring(/rdf:RDF/bf:Item/htrc:contentProviderAgent/@rdf:resource,52)" /><xsl:text>"</xsl:text>
					<xsl:text>, &#10;			"type": "Organization"</xsl:text>
					<xsl:text> &#10;		}</xsl:text>
				</xsl:if>
				<xsl:text>, &#10;		"mainEntityOfPage": [</xsl:text>
				<xsl:text> &#10;			"https://catalog.hathitrust.org/api/volumes/full/recordnumber/</xsl:text><xsl:value-of select="substring(/rdf:RDF/bf:Item/bf:itemOf/@rdf:resource,30)" /><xsl:text>.json"</xsl:text>
				<xsl:text>, &#10;			"https://catalog.hathitrust.org/api/volumes/brief/recordnumber/</xsl:text><xsl:value-of select="substring(/rdf:RDF/bf:Item/bf:itemOf/@rdf:resource,30)" /><xsl:text>.json"</xsl:text>
				<xsl:text>, &#10;			"https://catalog.hathitrust.org/api/volumes/full/htid/</xsl:text><xsl:value-of select="substring(/rdf:RDF/bf:Item/@rdf:about,28)" /><xsl:text>.json"</xsl:text>
				<xsl:text> &#10;		]</xsl:text>
				<xsl:call-template name="create_identifiers">
					<xsl:with-param name="subclass" select="'Lcc'" />
				</xsl:call-template>
				<xsl:call-template name="create_identifiers">
					<xsl:with-param name="subclass" select="'Lccn'" />
				</xsl:call-template>
				<xsl:if test="/rdf:RDF/bf:Instance/bf:genreForm/bf:GenreForm/rdfs:label">
					<xsl:text>, &#10;		"genre": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Instance/bf:genreForm/bf:GenreForm/rdfs:label/text()" /><xsl:text>"</xsl:text>
				</xsl:if>
				<xsl:if test="/rdf:RDF/bf:Item/bf:enumerationAndChronology">
					<xsl:text>, &#10;		"enumerationChronology": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Item/bf:enumerationAndChronology/text()" /><xsl:text>"</xsl:text>
				</xsl:if>
				<xsl:if test="/rdf:RDF/bf:Instance/bf:genreForm/bf:GenreForm/rdfs:label and /rdf:RDF/bf:Instance/bf:genreForm/bf:GenreForm/rdfs:label/text() = 'periodical'">
					<xsl:text>, &#10;		"isPartOf": {</xsl:text>
					<xsl:text> &#10;			"title": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Work/bf:title/bf:Title/rdfs:label/text()" /><xsl:text>"</xsl:text>
					<xsl:text>, &#10;			"isPartOf": {</xsl:text>
					<xsl:text> &#10;				"id": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Instance/@rdf:about" /><xsl:text>"</xsl:text>
					<xsl:text>, &#10;				"title": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Work/bf:title/bf:Title/rdfs:label/text()" /><xsl:text>"</xsl:text>
					<xsl:text>, &#10;				"type": "Periodical"</xsl:text>
					<xsl:if test="/rdf:RDF/bf:Instance/bf:identifiedBy/bf:Issn/rdf:value">
						<xsl:text>, &#10;				"issn": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Instance/bf:identifiedBy/bf:Issn/rdf:value/text()" /><xsl:text>"</xsl:text>
					</xsl:if>
					<xsl:text> &#10;			}</xsl:text>
					<xsl:text> &#10;		}</xsl:text>
				</xsl:if>
				<xsl:text> &#10;	}</xsl:text>
				<xsl:text>&#10;}</xsl:text>
		</xsl:result-document>
	</xsl:template>

	<xsl:template name="contribution_agents"><!-- match="/rdf:RDF/bf:Work/bf:contribution/bf:Contribution/">-->
		<xsl:param name="node" />
		<xsl:for-each select="$node">
			<xsl:choose>
				<xsl:when test="rdf:type/@rdf:resource = 'http://id.loc.gov/ontologies/bflc/PrimaryContribution'">
					<xsl:text>, &#10;		"author": {</xsl:text>
				</xsl:when>
				<xsl:otherwise>
					<xsl:text>, &#10;		"contributor": {</xsl:text>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:text> &#10;			"type": "</xsl:text><xsl:value-of select="substring(bf:agent/bf:Agent/rdf:type/@rdf:resource,39)" /><xsl:text>"</xsl:text>
			<xsl:text> &#10;			"id": "</xsl:text><xsl:value-of select="bf:agent/bf:Agent/@rdf:about" /><xsl:text>"</xsl:text>
			<xsl:text> &#10;			"name": "</xsl:text><xsl:value-of select="bf:agent/bf:Agent/rdfs:label/text()" /><xsl:text>"</xsl:text>
			<xsl:text> &#10;		}</xsl:text>
		</xsl:for-each>
	</xsl:template>

	<xsl:template name="create_identifiers">
		<xsl:param name="subclass" />
		<xsl:choose>
			<xsl:when test="$subclass = 'Lcc'">
				<xsl:if test="/rdf:RDF/bf:Work/bf:classification/bf:ClassificationLcc">
					<xsl:for-each select="/rdf:RDF/bf:Work/bf:classification/bf:ClassificationLcc">
						<xsl:text>, &#10;		"identifier": {</xsl:text>
						<xsl:text> &#10;			"type": "PropertyValue"</xsl:text>
						<xsl:text>, &#10;			"propertyID": "</xsl:text><xsl:value-of select="lower-case($subclass)" /><xsl:text>"</xsl:text>
						<xsl:text>, &#10;			"value": "</xsl:text><xsl:value-of select="./bf:classificationPortion/text()" /><xsl:text> </xsl:text><xsl:value-of select="./bf:itemPortion/text()" /><xsl:text>"</xsl:text>
						<xsl:text> &#10;		}</xsl:text>
					</xsl:for-each>
				</xsl:if>
			</xsl:when>
			<xsl:otherwise>
				<xsl:if test="/rdf:RDF/bf:Instance/bf:identifiedBy/*[name() = concat('bf:',$subclass)]/rdf:value">
					<xsl:for-each select="/rdf:RDF/bf:Instance/bf:identifiedBy/*[name() = concat('bf:',$subclass)]">
						<xsl:text>, &#10;		"identifier": {</xsl:text>
						<xsl:text> &#10;			"type": "PropertyValue"</xsl:text>
						<xsl:text>, &#10;			"propertyID": "</xsl:text><xsl:value-of select="lower-case($subclass)" /><xsl:text>"</xsl:text>
						<xsl:text>, &#10;			"value": "</xsl:text><xsl:value-of select="./rdf:value/text()" /><xsl:text>"</xsl:text>
						<xsl:text> &#10;		}</xsl:text>
					</xsl:for-each>
				</xsl:if>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
</xsl:stylesheet>