import requests, pyld, json
from rdflib import Graph, plugin
from rdflib.serializer import Serializer

def main():
	example_handle = 'http://hdl.handle.net/2027/uc1.l0079859914'
	with open('bibframe2ef.rq','r') as query_file:
		test_query = query_file.read()
	
	test_query = test_query.replace('?handle_url','<' + example_handle + '>')
	print(test_query)
	results = requests.post("https://worksets.htrc.illinois.edu/sparql/",data={'default_graph_uri': '', 'query': test_query, 'format': 'application/ld+json'})
#	print(results)
	print(results.text)
	context = [ 
		"http://schema.org/", 
		{ 
			"htrc": "http://wcsa.htrc.illinois.edu/", 
			"accessProfile": { 
				"@id": "htrc:accessProfile" 
			}, 
			"title": "name", 
			"enumerationChronology": { 
				"@id": "htrc:enumerationChronology" 
			}, 
			"pubDate": "datePublished", 
			"pubPlace": "locationCreated", 
			"language": "inLanguage", 
			"rightsAttributes": { 
				"@id": "htrc:accessRights" 
			}, 
			"contributor": { 
				"@id": "schema:contributor", 
				"@container": "@list" 
			}, 
			"sourceInstitution": "provider", 
			"lastUpdateDate": "dateModified", 
			"identifier": { 
				"@id": "schema:identifier", 
				"@container": "@list" 
			} 
		} 
	]
#	print(context)
#	jsonld = json.loads(results.text)
#	print(jsonld)
#	jsonld = pyld.jsonld.compact(jsonld,context)
#	print(jsonld)
#	g = Graph().parse(data=results.text, format='json-ld')
#	print(g.serialize(format='json-ld', context=context, indent=4))

main()