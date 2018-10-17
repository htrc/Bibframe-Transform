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

		<xsl:result-document href="ef_example2.jsonld" method='text' exclude-result-prefixes="#all" omit-xml-declaration="yes" indent="no" encoding="UTF-8">
<!--				<xsl:text>{ &#10;	"@context": [</xsl:text>
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
				<xsl:text>, &#10;	"sourceInstitution": "htrc"</xsl:text>-->
				<xsl:text>, &#10;	"metadata": {</xsl:text>
				<xsl:text> &#10;		"id": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Item/@rdf:about" /><xsl:text>"</xsl:text>
				<xsl:choose>
					<xsl:when test="substring(/rdf:RDF/bf:Instance/bf:issuance/bf:Issuance/@rdf:about,39) = 'mono'">
						<xsl:text>, &#10;		"type": "Book"</xsl:text>
					</xsl:when>
					<xsl:otherwise>
						<xsl:choose>
							<xsl:when test="substring(/rdf:RDF/bf:Instance/bf:issuance/bf:Issuance/@rdf:about,39) = 'serl'">
								<xsl:text>, &#10;		"type": "PublicationVolume"</xsl:text>
							</xsl:when>
							<xsl:otherwise>
								<xsl:text>, &#10;		"type": "CreativeWork"</xsl:text>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:otherwise>
				</xsl:choose>
<!--				<xsl:text>, &#10;		"type": "</xsl:text><xsl:value-of select="substring(/rdf:RDF/bf:Instance/bf:issuance/bf:Issuance/@rdf:about,39)" /><xsl:text>"</xsl:text>-->
				<xsl:text>, &#10;		"isAccessibleForFree": </xsl:text>
					<xsl:choose>
						<xsl:when test="/rdf:RDF/bf:Item/dct:accessRights/text() = 'pd'">
							<xsl:text>true</xsl:text>
						</xsl:when>
						<xsl:otherwise>
							<xsl:text>false</xsl:text>
						</xsl:otherwise>
					</xsl:choose>
				<xsl:text>, &#10;		"title": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Work/bf:title/bf:Title/rdfs:label/text()" /><xsl:text>"</xsl:text>
				<xsl:call-template name="contribution_agents">
					<xsl:with-param name="node" select="/rdf:RDF/bf:Work/bf:contribution/bf:Contribution" />
				</xsl:call-template>
				<xsl:if test="/rdf:RDF/bf:Instance/bf:provisionActivity/bf:ProvisionActivity/bf:date">
					<xsl:text>, &#10;		"pubDate": </xsl:text><xsl:value-of select="substring(/rdf:RDF/bf:Instance/bf:provisionActivity/bf:ProvisionActivity/bf:date[1]/text(),1,4)" />
				</xsl:if>
				<xsl:if test="/rdf:RDF/bf:Instance/bf:provisionActivity/bf:ProvisionActivity/bf:agent/bf:Agent/rdfs:label">
					<xsl:text>, &#10;		"publisher": {</xsl:text>
					<xsl:text> &#10;			"type": "http://id.loc.gov/ontologies/bibframe/Organization"</xsl:text>
					<xsl:text>, &#10;			"name": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Instance/bf:provisionActivity/bf:ProvisionActivity/bf:agent/bf:Agent/rdfs:label/text()" /><xsl:text>"</xsl:text>
					<xsl:text> &#10;		}</xsl:text>
				</xsl:if>
				<xsl:call-template name="pub_place" />
<!--				<xsl:choose>
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
				</xsl:choose>-->
				<xsl:call-template name="languages" />
<!--				<xsl:choose>
					<xsl:when test="/rdf:RDF/bf:Work/bf:language/bf:Language/bf:identifiedBy/bf:Identifier/rdf:value/@rdf:resource">
						<xsl:choose>
							<xsl:when test="count(/rdf:RDF/bf:Work/bf:language/bf:Language/bf:identifiedBy/bf:Identifier/rdf:value/@rdf:resource) > 1">
								<xsl:text>, &#10;		"inLanguage": [</xsl:text>
								<xsl:for-each select="/rdf:RDF/bf:Work/bf:language/bf:Language/bf:identifiedBy/bf:Identifier/rdf:value/@rdf:resource">
									<xsl:text> &#10;			"</xsl:text><xsl:value-of select="substring(.,40)" /><xsl:text>"</xsl:text>
									<xsl:if test="position() != last()">
										<xsl:text>, </xsl:text>
									</xsl:if>
								</xsl:for-each>
								<xsl:text> &#10;		]</xsl:text>
							</xsl:when>
							<xsl:otherwise>
								<xsl:text>, &#10;		"inLanguage": "</xsl:text><xsl:value-of select="substring(/rdf:RDF/bf:Work/bf:language/bf:Language/bf:identifiedBy/bf:Identifier/rdf:value/@rdf:resource,40)" /><xsl:text>"</xsl:text>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:when>
					<xsl:otherwise>
						<xsl:if test="/rdf:RDF/bf:Work/bf:language/bf:Language/@rdf:about">
							<xsl:text>, &#10;		"inLanguage": "</xsl:text><xsl:value-of select="substring(/rdf:RDF/bf:Work/bf:language/bf:Language/@rdf:about,40)" /><xsl:text>"</xsl:text>
						</xsl:if>
					</xsl:otherwise>
				</xsl:choose>-->
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
				<xsl:text> &#10;			"http://catalog.hathitrust.org/api/volumes/full/oclc/</xsl:text><xsl:value-of select="substring(/rdf:RDF/bf:Item/bf:itemOf/@rdf:resource,30)" /><xsl:text>.json"</xsl:text>
				<xsl:text>, &#10;			"http://catalog.hathitrust.org/api/volumes/brief/oclc/</xsl:text><xsl:value-of select="substring(/rdf:RDF/bf:Item/bf:itemOf/@rdf:resource,30)" /><xsl:text>.json"</xsl:text>
				<xsl:text>, &#10;			"https://catalog.hathitrust.org/Record/</xsl:text><xsl:value-of select="/rdf:RDF/bf:Work/bf:adminMetadata/bf:AdminMetadata/bf:identifiedBy/bf:Local/rdf:value/text()" /><xsl:text>"</xsl:text>
				<xsl:text> &#10;		]</xsl:text>
				<xsl:call-template name="create_identifiers" />
				<xsl:if test="/rdf:RDF/bf:Instance/bf:identifiedBy/bf:Issn/rdf:value">
					<xsl:text>, &#10;		"issn": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Instance/bf:identifiedBy/bf:Issn/rdf:value/text()" /><xsl:text>"</xsl:text>
				</xsl:if>
				<xsl:if test="/rdf:RDF/bf:Instance/bf:identifiedBy/bf:Isbn/rdf:value">
					<xsl:text>, &#10;		"issn": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Instance/bf:identifiedBy/bf:Isbn/rdf:value/text()" /><xsl:text>"</xsl:text>
				</xsl:if>
				<xsl:if test="/rdf:RDF/bf:Work/bf:genreForm/bf:GenreForm/@rdf:about">
					<xsl:variable name="genre_count" select="count(/rdf:RDF/bf:Work/bf:genreForm/bf:GenreForm/@rdf:about)" />
					<xsl:choose>
						<xsl:when test="$genre_count = 1">
							<xsl:text>, &#10;		"genre": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Work/bf:genreForm/bf:GenreForm/@rdf:about" /><xsl:text>"</xsl:text>
						</xsl:when>
						<xsl:otherwise>
							<xsl:if test="$genre_count > 1">
								<xsl:text>, &#10;		"genre": [</xsl:text>
								<xsl:for-each select="/rdf:RDF/bf:Work/bf:genreForm/bf:GenreForm/@rdf:about">
									<xsl:if test="position() != 1">
										<xsl:text>,</xsl:text>
									</xsl:if>
									<xsl:text> &#10;			"</xsl:text><xsl:value-of select="." /><xsl:text>"</xsl:text>
								</xsl:for-each>
								<xsl:text> &#10;		]</xsl:text>
							</xsl:if>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:if>
				<xsl:if test="/rdf:RDF/bf:Item/bf:enumerationAndChronology">
					<xsl:text>, &#10;		"enumerationChronology": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Item/bf:enumerationAndChronology/text()" /><xsl:text>"</xsl:text>
				</xsl:if>
				<xsl:if test="/rdf:RDF/bf:Instance/bf:genreForm/bf:GenreForm/rdfs:label and /rdf:RDF/bf:Instance/bf:genreForm/bf:GenreForm/rdfs:label/text() = 'periodical'">
					<xsl:if test="matches(/rdf:RDF/bf:Item/bf:enumerationAndChronology/text(),'no.')">
						<xsl:text>, &#10;		"issueNumber": "</xsl:text>
						<xsl:choose>
							<xsl:when test="matches(/rdf:RDF/bf:Item/bf:enumerationAndChronology/text(),'-[: ]?v.')">
								<xsl:text>no.</xsl:text><xsl:value-of select="tokenize(tokenize(/rdf:RDF/bf:Item/bf:enumerationAndChronology/text(),'-[: ]?v.')[1],'no.')[2]" /><xsl:text>-</xsl:text><xsl:text>no.</xsl:text><xsl:value-of select="tokenize(tokenize(/rdf:RDF/bf:Item/bf:enumerationAndChronology/text(),'-[: ]?v.')[last()],'no.')[2]" />
							</xsl:when>
							<xsl:otherwise>
								<xsl:text>no.</xsl:text><xsl:value-of select="tokenize(/rdf:RDF/bf:Item/bf:enumerationAndChronology/text(),'no.')[2]" />
							</xsl:otherwise>
						</xsl:choose>
						<xsl:text>"</xsl:text>
					</xsl:if>
					<xsl:text>, &#10;		"isPartOf": {</xsl:text>
					<xsl:text> &#10;			"title": "</xsl:text><xsl:value-of select="/rdf:RDF/bf:Work/bf:title/bf:Title/rdfs:label/text()" /><xsl:text>"</xsl:text>
					<xsl:if test="/rdf:RDF/bf:Item/bf:enumerationAndChronology">
						<xsl:text> &#10;			"enumerationChronology": "</xsl:text>
						<xsl:choose>
							<xsl:when test="matches(/rdf:RDF/bf:Item/bf:enumerationAndChronology/text(),'-[: ]?v.')">
								<xsl:value-of select="normalize-space(tokenize(tokenize(/rdf:RDF/bf:Item/bf:enumerationAndChronology/text(),'-[: ]?v.')[1],'no.')[1])" /><xsl:text>-</xsl:text><xsl:text>v.</xsl:text><xsl:value-of select="normalize-space(tokenize(tokenize(/rdf:RDF/bf:Item/bf:enumerationAndChronology/text(),'-[: ]?v.')[last()],'no.')[1])" />
							</xsl:when>
							<xsl:otherwise>
								<xsl:value-of select="tokenize(/rdf:RDF/bf:Item/bf:enumerationAndChronology/text(),'no.')[1]" />
							</xsl:otherwise>
						</xsl:choose>
					</xsl:if>
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
		<xsl:variable name="contributor_count" select="count($node)" />
		<xsl:choose>
			<xsl:when test="$contributor_count = 1">
				<xsl:text>, &#10;		"contributor": {</xsl:text>
				<xsl:text> &#10;			"type": "</xsl:text><xsl:value-of select="$node/bf:agent/bf:Agent/rdf:type/@rdf:resource" /><xsl:text>"</xsl:text>
				<xsl:text>, &#10;			"id": "</xsl:text><xsl:value-of select="$node/bf:agent/bf:Agent/@rdf:about" /><xsl:text>"</xsl:text>
				<xsl:text>, &#10;			"name": "</xsl:text><xsl:value-of select="$node/bf:agent/bf:Agent/rdfs:label/text()" /><xsl:text>"</xsl:text>
				<xsl:text> &#10;		}</xsl:text>
			</xsl:when>
			<xsl:otherwise>
				<xsl:if test="$contributor_count > 1">
					<xsl:text>, &#10;		"contributor": [</xsl:text>
					<xsl:for-each select="$node">
						<xsl:if test="position() != 1">
							<xsl:text>,</xsl:text>
						</xsl:if>
						<xsl:text> &#10;			{</xsl:text>
						<xsl:text> &#10;				"type": "</xsl:text><xsl:value-of select="bf:agent/bf:Agent/rdf:type/@rdf:resource" /><xsl:text>"</xsl:text>
						<xsl:text>, &#10;				"id": "</xsl:text><xsl:value-of select="bf:agent/bf:Agent/@rdf:about" /><xsl:text>"</xsl:text>
						<xsl:text>, &#10;				"name": "</xsl:text><xsl:value-of select="bf:agent/bf:Agent/rdfs:label/text()" /><xsl:text>"</xsl:text>
						<xsl:text> &#10;			}</xsl:text>
					</xsl:for-each>
					<xsl:text> &#10;		]</xsl:text>
				</xsl:if>
			</xsl:otherwise>
		</xsl:choose>
<!--		<xsl:for-each select="$node">
			<xsl:text>, &#10;		"contributor": {</xsl:text>
			<xsl:text> &#10;			"type": "</xsl:text><xsl:value-of select="bf:agent/bf:Agent/rdf:type/@rdf:resource" /><xsl:text>"</xsl:text>
			<xsl:text> &#10;			"id": "</xsl:text><xsl:value-of select="bf:agent/bf:Agent/@rdf:about" /><xsl:text>"</xsl:text>
			<xsl:text> &#10;			"name": "</xsl:text><xsl:value-of select="bf:agent/bf:Agent/rdfs:label/text()" /><xsl:text>"</xsl:text>
			<xsl:text> &#10;		}</xsl:text>
		</xsl:for-each>-->
	</xsl:template>

	<xsl:template name="pub_place">
		<xsl:variable name="pub_places" select="/rdf:RDF/bf:Instance/bf:provisionActivity/bf:ProvisionActivity/bf:place/bf:Place/@rdf:about" />
		<xsl:choose>
			<xsl:when test="count($pub_places) > 1" >
				<xsl:text>, &#10;		"pubPlace": [</xsl:text>
				<xsl:for-each select="$pub_places">
					<xsl:if test="position() != 1">
						<xsl:text>,</xsl:text>
					</xsl:if>
					<xsl:text> &#10;			{</xsl:text>
					<xsl:text> &#10;				"id": "</xsl:text><xsl:value-of select="." /><xsl:text>"</xsl:text>
					<xsl:text>, &#10;				"type": "http://id.loc.gov/ontologies/bibframe/Place"</xsl:text>
					<xsl:text> &#10;			}</xsl:text>
				</xsl:for-each>
				<xsl:text> &#10;		]</xsl:text>
			</xsl:when>
			<xsl:otherwise>
				<xsl:if test="count($pub_places) = 1">
					<xsl:text>, &#10;		"pubPlace": {</xsl:text>
					<xsl:text> &#10;			"id": "</xsl:text><xsl:value-of select="$pub_places" /><xsl:text>"</xsl:text>
					<xsl:text>, &#10;			"type": "http://id.loc.gov/ontologies/bibframe/Place"</xsl:text>
					<xsl:text> &#10;		}</xsl:text>
				</xsl:if>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="languages">
		<xsl:variable name="lang_strs" select="/rdf:RDF/bf:Work/bf:language/bf:Language/@rdf:about" />
		<xsl:variable name="lang_nodes" select="/rdf:RDF/bf:Work/bf:language/bf:Language/bf:identifiedBy/bf:Identifier/rdf:value/@rdf:resource" />
		<xsl:variable name="lang_strs_count" select="count($lang_strs)" />
		<xsl:variable name="lang_nodes_count" select="count($lang_nodes)" />
		<xsl:variable name="lang_count" select="$lang_strs_count + $lang_nodes_count" />
		<xsl:choose>
			<xsl:when test="$lang_count > 1">
				<xsl:variable name="lang_combined" select="/rdf:RDF/bf:Work/bf:language/bf:Language/@rdf:about | /rdf:RDF/bf:Work/bf:language/bf:Language/bf:identifiedBy/bf:Identifier/rdf:value/@rdf:resource" />
				<xsl:text>, &#10;		"inLanguage": [</xsl:text>
				<xsl:for-each select="distinct-values($lang_combined)">
					<xsl:if test="position() != 1">
						<xsl:text>,</xsl:text>
					</xsl:if>
					<xsl:text> &#10;			"</xsl:text><xsl:value-of select="substring(.,40)" /><xsl:text>"</xsl:text>
				</xsl:for-each>
				<xsl:text> &#10;		]</xsl:text>
			</xsl:when>
			<xsl:otherwise>
				<xsl:if test="$lang_count = 1">
					<xsl:text>, &#10;		"inLanguage": "</xsl:text>
					<xsl:choose>
						<xsl:when test="$lang_strs_count = 1">
							<xsl:value-of select="substring($lang_strs,40)" /><xsl:text>"</xsl:text>
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="substring($lang_nodes,40)" /><xsl:text>"</xsl:text>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:if>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="create_identifiers">
		<xsl:variable name="lcc" select="/rdf:RDF/bf:Work/bf:classification/bf:ClassificationLcc" />
		<xsl:variable name="lccn" select="/rdf:RDF/bf:Instance/bf:identifiedBy/bf:Lccn/rdf:value" />
		<xsl:variable name="oclc" select="/rdf:RDF/bf:Instance/bf:identifiedBy/bf:Local[bf:source/bf:Source/rdfs:label = 'OCoLC']" />
		<xsl:variable name="lcc_count" select="count($lcc)" />
		<xsl:variable name="lccn_count" select="count($lccn)" />
		<xsl:variable name="oclc_count" select="count($oclc)" />
		<xsl:variable name="identifier_count" select="$lcc_count + $lccn_count + $oclc_count" />
		<xsl:choose>
			<xsl:when test="$identifier_count = 1">
				<xsl:text>, &#10;		"identifier": {</xsl:text>
				<xsl:text> &#10;			"type": "PropertyValue"</xsl:text>
				<xsl:choose>
					<xsl:when test="$lcc_count = 1">
						<xsl:text>, &#10;			"propertyID": "lcc"</xsl:text>
						<xsl:text>, &#10;			"value": "</xsl:text><xsl:value-of select="$lcc/bf:classificationPortion/text()" /><xsl:text> </xsl:text><xsl:value-of select="$lcc/bf:itemPortion/text()" /><xsl:text>"</xsl:text>
					</xsl:when>
					<xsl:otherwise>
						<xsl:choose>
							<xsl:when test="$lccn_count = 1">
								<xsl:text>, &#10;			"propertyID": "lccn"</xsl:text>
								<xsl:text>, &#10;			"value": "</xsl:text><xsl:value-of select="$lccn/text()" /><xsl:text>"</xsl:text>
							</xsl:when>
							<xsl:otherwise>
								<xsl:text>, &#10;			"propertyID": "oclc"</xsl:text>
								<xsl:text>, &#10;			"value": "</xsl:text><xsl:value-of select="$oclc/rdf:value/text()" /><xsl:text>"</xsl:text>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:otherwise>
				</xsl:choose>
				<xsl:text> &#10;		}</xsl:text>
			</xsl:when>
			<xsl:otherwise>
				<xsl:if test="$identifier_count > 1">
					<xsl:text>, &#10;		"identifier": [</xsl:text>
					<xsl:for-each select="$lcc">
						<xsl:if test="position() != 1">
							<xsl:text>,</xsl:text>
						</xsl:if>
						<xsl:text> &#10;			{</xsl:text>
						<xsl:text> &#10;				"type": "PropertyValue"</xsl:text>
						<xsl:text>, &#10;				"propertyID": lcc"</xsl:text>
						<xsl:text>, &#10;				"value": "</xsl:text><xsl:value-of select="./bf:classificationPortion/text()" /><xsl:text> </xsl:text><xsl:value-of select="./bf:itemPortion/text()" /><xsl:text>"</xsl:text>
						<xsl:text> &#10;			}</xsl:text>
					</xsl:for-each>
					<xsl:for-each select="$lccn">
						<xsl:if test="position() != 1 or $lcc_count > 0">
							<xsl:text>,</xsl:text>
						</xsl:if>
						<xsl:text> &#10;			{</xsl:text>
						<xsl:text> &#10;				"type": "PropertyValue"</xsl:text>
						<xsl:text>, &#10;				"propertyID": lccn"</xsl:text>
						<xsl:text>, &#10;				"value": "</xsl:text><xsl:value-of select="./text()" /><xsl:text>"</xsl:text>
						<xsl:text> &#10;			}</xsl:text>
					</xsl:for-each>
					<xsl:for-each select="$oclc">
						<xsl:if test="position() != 1 or $lcc_count + $lccn_count > 0">
							<xsl:text>,</xsl:text>
						</xsl:if>
						<xsl:text> &#10;			{</xsl:text>
						<xsl:text> &#10;				"type": "PropertyValue"</xsl:text>
						<xsl:text>, &#10;				"propertyID": oclc"</xsl:text>
						<xsl:text>, &#10;				"value": "</xsl:text><xsl:value-of select="./rdf:value/text()" /><xsl:text>"</xsl:text>
						<xsl:text> &#10;			}</xsl:text>
					</xsl:for-each>
					<xsl:text> &#10;		]</xsl:text>
				</xsl:if>
			</xsl:otherwise>
		</xsl:choose>
<!--		<xsl:choose>
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
		</xsl:choose>-->
	</xsl:template>
</xsl:stylesheet>