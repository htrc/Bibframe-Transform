import os, sys, requests, time, urllib, json, uuid, re
import HTMLParser
from lxml import etree
from unicodedata import normalize
from mysql.connector import MySQLConnection

class BrokenResponse:
	status_code = '404'

def sanitizeMatchString(match_string):
	if match_string[-1:] != '.' and match_string[-1:] != '-':
		return match_string
	else:
		return sanitizeMatchString(match_string[:-1])

def convertFillerURI(filler_uri):
	base = filler_uri[filler_uri.rfind('/')+1:filler_uri.rfind('#')]
	end_string = filler_uri[filler_uri.rfind('#')+1:]
	if '-' in end_string:
		dash_index = end_string.rfind('-')
		end_string = end_string[:dash_index] + end_string[dash_index+1:]

	match = re.match(r"([a-zA-Z]+)([0-9]*)",end_string)
	if match:
		items = match.groups()
		if items[0] == 'Work':
			text_conversion = '0'
		elif items[0] == 'Instance':
			text_conversion = '1'
		elif items[0] == 'Agent':
			text_conversion = '2'
		elif items[0] == 'GenreForm':
			text_conversion = '3'
		else:
			text_conversion = '4'

		return '_:b' + base + text_conversion + items[1]
	else:
		return '_:b' + base

def createBlankNode(agent):
	try:
		return agent.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about',convertFillerURI(agent.xpath('./@rdf:about',namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#" })[0]))
	except IndexError:
		return agent.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about','_:b' + str(uuid.uuid1().int))

def normalizeVariant(variant):
	if isinstance(variant,str):
		return variant.strip()
	elif isinstance(variant,unicode):
		return variant.encode('utf-8').strip()

def getRequest(url,expectJSON):
	if 'viaf.org' in url:
		try:
			h = HTMLParser.HTMLParser()
			splitpoint = url.find('?query=')+7
			url = url[:splitpoint] + h.unescape(url[splitpoint:])
			print(url)
		except UnicodeDecodeError:
			h = HTMLParser.HTMLParser()
			splitpoint = url.find('?query=')+7
			url = url[:splitpoint] + h.unescape(url[splitpoint:].decode('utf-8'))
			print(url)         
		except:
			raise

		error_case = '<'
	else:
		error_case = '<html>\n<head><title>Temporarily out of service</title>'

	try:
		result = requests.get(url,timeout=60)
		if expectJSON:
			check_json = result.json()
	except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, ValueError) as e:
		result = BrokenResponse()

	if result.status_code == 403:
		return None

	print(result)
	while result.status_code != 200 or result.content.find(error_case) == 0:
		print(result.status_code)
		time.sleep(6)
		try:
			result = requests.get(url,timeout=60)
			if expectJSON:
				check_json = result.json()
		except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, ValueError) as e:
			result = BrokenResponse()

		print(result)

	print(result.content)
	print(type(result.content))
	return result

#Sets @rdf:about for bf:Work and @rdf:resource for bf:Instance/bf:instanceOf to the instance's OCLC record's 'exampleOfWork' value
def setWorkURLs(work,instance,placeholder_work_id,instance_url,last_loaded_worldcat_record):
	print(instance_url)
	if last_loaded_worldcat_record is None or last_loaded_worldcat_record['url'] != instance_url:
		if 'worldcat.org' in instance_url:
			result = getRequest(instance_url + '.jsonld',True)
#            result = requests.get(instance_url + '.jsonld')
#            while result.status_code != 200:
#                print(result.status_code)
#                time.sleep(6)
#                try:
#                    result = requests.get(instance_url + '.jsonld')
#                except requests.exceptions.ConnectionError:
#                    result = { 'status_code': '404' }

			if result:
				print(result.content)
				result = result.json()
				print(result['@graph'])
				for r in result['@graph']:
					if 'exampleOfWork' in r:
						work.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about',r['exampleOfWork'])
						instance.xpath("./bf:instanceOf[@rdf:resource='" + placeholder_work_id + "']", namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })[0].set("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource",r['exampleOfWork'])

				return { 'url': instance_url, 'record': result }
			else:
				return None
		else:
			work.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about', instance_url + "1")
			instance.xpath("./bf:instanceOf[@rdf:resource='" + placeholder_work_id + "']", namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })[0].set("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource",instance_url + "1")
			return None
	else:
		print("BENEFIT")
		for r in last_loaded_worldcat_record['record']['@graph']:
			if 'exampleOfWork' in r:
				work.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about',r['exampleOfWork'])
				instance.xpath("./bf:instanceOf[@rdf:resource='" + placeholder_work_id + "']", namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })[0].set("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource",r['exampleOfWork'])

		return last_loaded_worldcat_record

def getAgentTypes(agent_types,target_domain):
	if 'http://id.loc.gov/ontologies/bibframe/Organization' in agent_types:
		return ('CorporateName' if target_domain == 'id.loc.gov' else 'corporate'), 'name10MatchKey', 'subjects'
	elif 'http://id.loc.gov/ontologies/bibframe/Person' in agent_types or 'http://www.loc.gov/mads/rdf/v1#Name' in agent_types:
		return ('PersonalName' if target_domain == 'id.loc.gov' else 'personal'), 'name00MatchKey', 'names'
	elif 'http://id.loc.gov/ontologies/bibframe/Meeting' in agent_types or 'http://www.loc.gov/mads/rdf/v1#ConferenceName' in agent_types:
		return ('ConferenceName' if target_domain == 'id.loc.gov' else 'corporate'), 'name11MatchKey', 'names'
	elif 'http://id.loc.gov/ontologies/bibframe/Jurisdiction' in agent_types:
		return ('CorporateName' if target_domain == 'id.loc.gov' else 'corporate'), 'name10MatchKey', 'names'
	elif 'http://id.loc.gov/ontologies/bibframe/Family' in agent_types:
		return ('FamilyName' if target_domain == 'id.loc.gov' else 'personal'), 'name00MatchKey', 'subjects'
	elif 'http://www.loc.gov/mads/rdf/v1#Topic' in agent_types:
		return 'Topic', 'authoritativeLabel', 'subjects'
	elif 'http://www.loc.gov/mads/rdf/v1#Geographic' in agent_types:
		return 'Geographic', 'authoritativeLabel', 'subjects'
	elif 'http://www.loc.gov/mads/rdf/v1#Title' in agent_types:
		return 'Title', 'authoritativeLabel', 'names'
	elif 'http://www.loc.gov/mads/rdf/v1#NameTitle' in agent_types:
		return 'NameTitle', 'authoritativeLabel', 'names'
	elif 'http://www.loc.gov/mads/rdf/v1#HierarchicalGeographic' in agent_types:
		return 'ComplexSubject', 'label', 'subjects'
	elif agent_types[0] == 'http://www.loc.gov/mads/rdf/v1#ComplexSubject':
		return 'ComplexSubject', 'authoritativeLabel', 'subjects'
	else:
		print("FOUND UNHANDLED SUBJECT TYPE:")
		print(agent_types)
		sys.exit()

#Search id.loc.gov for an exact subject match, assign the url of that subject to bf:Agent/@rdf:about, remember subjects that have been 
#   retrieved in a dictionary that can be referenced instead of redundantly calling id.loc.gov again
def setSubjectAgent(agent,merged_subject_agents):
	BASE_LC_URL = 'https://id.loc.gov/search/?q='
	agent_types = agent.xpath("./rdf:type/@rdf:resource",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#" })
	agent_type = None
	if agent_types:
		agent_type, match_key_type, search_type = getAgentTypes(agent_types,'id.loc.gov')

	print('V---SUBJECT AGENT--SUBJECT AGENT--SUBJECT AGENT--SUBJECT AGENT--SUBJECT AGENT----V')
	if agent_type:
		match_key = agent.xpath("./bflc:" + match_key_type + "/text()", namespaces={ "bflc": "http://id.loc.gov/ontologies/bflc/" })
		if len(match_key) > 0:
			match_key = match_key[0]
		else:
			match_key = agent.xpath("./rdfs:label/text()", namespaces={ "rdfs": "http://www.w3.org/2000/01/rdf-schema#" })
			if len(match_key) > 0:
				match_key = match_key[0]
			else:
				match_key = None

		if match_key:
			match_key = sanitizeMatchString(match_key.encode('utf-8'))

		if match_key and match_key not in merged_subject_agents:
			print(match_key)
			query_url = BASE_LC_URL + urllib.quote_plus(match_key) + '+rdftype:' + agent_type + '&q=cs%3Ahttp%3A%2F%2Fid.loc.gov%2Fauthorities%2F' + search_type
			print(query_url)
#            results_tree = etree.HTML(requests.get(query_url).content)
			results_tree = etree.HTML(getRequest(query_url,False).content)
			result_table = results_tree.xpath("//table[@class='id-std']/tbody/tr")
			match_not_found = True
			i = 0
			while i < len(result_table) and match_not_found:
				authorized_name = result_table[i].xpath("./td/a/text()")
				print(authorized_name)
				variant_names = result_table[i+1].xpath("./td[@colspan='4']/text()")
				print(variant_names)
				if len(variant_names) > 0:
					variant_names = map(normalizeVariant,variant_names[0].split(';'))
				print(variant_names)
				print(match_key, authorized_name[0])
				print(match_key == authorized_name[0])

				if match_key in authorized_name or match_key in variant_names:
					print("Found " + match_key)
					subject_uri = 'http://id.loc.gov' + result_table[i].xpath("./td/a/@href")[0]
					print(subject_uri)
					agent.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about',subject_uri)
					match_not_found = False
					merged_subject_agents[authorized_name[0]] = { 'agent_type': agent_type, 'uri': subject_uri }
					for variant in variant_names:
						merged_subject_agents[variant] = merged_subject_agents[authorized_name[0]]
				i = i + 2

			if match_not_found:
				merged_subject_agents[match_key] = None
				createBlankNode(agent)
		else:
			if match_key and merged_subject_agents[match_key] is not None:
				if merged_subject_agents[match_key]['agent_type'] == agent_type:
					agent.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about',merged_subject_agents[match_key]['uri'])
				else:
					createBlankNode(agent)
			else:
				createBlankNode(agent)

	print('^---SUBJECT AGENT--SUBJECT AGENT--SUBJECT AGENT--SUBJECT AGENT--SUBJECT AGENT----^')

def setTopicAgent(agent,merged_topic_agents,cursor):
	BASE_LC_URL = 'https://id.loc.gov/search/?q='
	agent_types = agent.xpath("./rdf:type/@rdf:resource",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#" })
	agent_type = None
	if agent_types:
		agent_type, match_key_type, search_type = getAgentTypes(agent_types,'id.loc.gov')

	print('V--TOPIC--TOPIC--TOPIC--TOPIC--TOPIC--TOPIC--TOPIC--TOPIC--TOPIC--TOPIC--TOPIC---V')
	if agent_type:
		match_key = agent.xpath("./madsrdf:" + match_key_type + "/text()", namespaces={ "madsrdf": "http://www.loc.gov/mads/rdf/v1#" })
		if len(match_key) > 0:
			match_key = match_key[0]
		else:
			match_key = agent.xpath("./rdfs:label/text()", namespaces={ "rdfs": "http://www.w3.org/2000/01/rdf-schema#" })
			if len(match_key) > 0:
				match_key = match_key[0]
			else:
				match_key = None

		if match_key:
			match_key = sanitizeMatchString(match_key.replace('"','\\"').encode('utf-8'))
			print(match_key)

			found_topic_url = False
			topic_url = None

			cursor.execute('SELECT * FROM Subject WHERE label = "' + match_key + '" AND concept_type = "http://www.loc.gov/mads/rdf/v1#' + agent_type + '"')
			for table in cursor:
				agent.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about',table[0])
				found_topic_url = True
				topic_url = table[0]

			if not found_topic_url:
				cursor.execute('SELECT * FROM Variant_Name WHERE variant_name = "' + match_key + '"')
				for table in cursor:
					agent.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about',table[0])
					found_topic_url = True
					topic_url = table[0]

			if found_topic_url:
				if agent_type == 'ComplexSubject':
					output_component_list = agent.xpath("./madsrdf:componentList/*",namespaces={ "madsrdf": "http://www.loc.gov/mads/rdf/v1#" })
					print("Output Component List:")
					print(output_component_list)

					if output_component_list:
						cursor.execute('SELECT * FROM Component WHERE source_url = "' + topic_url + '"')
						for table in cursor:
							output_component_list[table[1]].set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about',table[2])
			else:
				if match_key in merged_topic_agents:
					if merged_topic_agents[match_key] is not None:
						if merged_topic_agents[match_key]['agent_type'] == agent_type:
							agent.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about',merged_topic_agents[match_key]['uri'])
						else:
							createBlankNode(agent)
					else:
						createBlankNode(agent)
				else:
					query_url = BASE_LC_URL + urllib.quote_plus(match_key) + '+rdftype:' + agent_type + '&q=cs%3Ahttp%3A%2F%2Fid.loc.gov%2Fauthorities%2F' + search_type
					print(query_url)

					results_tree = etree.HTML(getRequest(query_url,False).content)
					result_table = results_tree.xpath("//table[@class='id-std']/tbody/tr")
					match_not_found = True
					i = 0
					while i < len(result_table) and match_not_found:
						authorized_heading = result_table[i].xpath("./td/a/text()")
						print(authorized_heading)
						variant_headings = result_table[i+1].xpath("./td[@colspan='4']/text()")
						print(variant_headings)
						if len(variant_headings) > 0:
							variant_headings = map(normalizeVariant,variant_headings[0].split(';'))
						print(variant_headings)
						print(match_key, authorized_heading[0])
						print(match_key == authorized_heading[0])

						if match_key in authorized_heading or match_key in variant_headings:
							print("Found " + match_key)
							subject_uri = 'http://id.loc.gov' + result_table[i].xpath("./td/a/@href")[0]
							print(subject_uri)
							agent.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about',subject_uri)
							match_not_found = False
							merged_topic_agents[authorized_heading[0]] = { 'agent_type': agent_type, 'uri': subject_uri }
							for variant in variant_headings:
								merged_topic_agents[variant] = merged_topic_agents[authorized_heading[0]]

							if agent_type == 'ComplexSubject':
								components_uri = subject_uri + '.madsrdf.rdf'
								print(components_uri)

								component_tree = etree.fromstring(getRequest(components_uri,False).content)
								component_list = component_tree.xpath("/rdf:RDF/madsrdf:ComplexSubject/madsrdf:componentList/*",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "madsrdf": "http://www.loc.gov/mads/rdf/v1#" })
								print("Component List:")
								print(component_list)

								output_component_list = agent.xpath("./madsrdf:componentList/*",namespaces={ "madsrdf": "http://www.loc.gov/mads/rdf/v1#" })
								print("Output Component List:")
								print(output_component_list)

								j = 0
								while j < len(component_list):
									component_url = component_list[j].xpath("./@rdf:about",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#" })
									if component_url:
										output_component_list[j].set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about',component_url[0])
									j = j + 1
							#http://id.loc.gov/authorities/subjects/sh2002011373.madsrdf.rdf
						i = i + 2

					if match_not_found:
						merged_topic_agents[match_key] = None
						createBlankNode(agent)

	print('^--TOPIC--TOPIC--TOPIC--TOPIC--TOPIC--TOPIC--TOPIC--TOPIC--TOPIC--TOPIC--TOPIC---^')

def setContributionAgent(agent,merged_contribution_agents):
	BASE_VIAF_URL = 'http://www.viaf.org/viaf/AutoSuggest?query='
	agent_types = agent.xpath("./rdf:type/@rdf:resource",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#" })
	agent_type = None
	if agent_types:
		agent_type, match_key_type, search_type = getAgentTypes(agent_types,'viaf.org')

	print('V-CONTRIBUTION AGENT--CONTRIBUTION AGENT--CONTRIBUTION AGENT--CONTRIBUTION AGENT-V')
	if agent_type:
		match_key = agent.xpath("./bflc:" + match_key_type + "/text()", namespaces={ "bflc": "http://id.loc.gov/ontologies/bflc/" })
		if len(match_key) > 0:
			match_key = match_key[0]
		else:
			match_key = agent.xpath("./rdfs:label/text()", namespaces={ "rdfs": "http://www.w3.org/2000/01/rdf-schema#" })
			if len(match_key) > 0:
				match_key = match_key[0]
			else:
				match_key = None

		if match_key:
			match_key = sanitizeMatchString(match_key.encode('utf-8'))

		if match_key not in merged_contribution_agents:
			print(match_key)
			query_url = BASE_VIAF_URL + match_key.replace('"',"'")
			print(query_url)
#            results = requests.get(query_url).content
			results = getRequest(query_url,True).content

			match_not_found = True

			results_dict = json.loads(results)
			print(results_dict)
			if results_dict['result']:
				i = 0
				while i < len(results_dict['result']) and match_not_found:
					print(results_dict['result'][i]['term'] == match_key.decode('utf-8'))
					print(results_dict['result'][i]['term'])
					print(match_key.decode('utf-8'))
					print(sanitizeMatchString(normalize('NFC',results_dict['result'][i]['term'])) == normalize('NFC',match_key.decode('utf-8')))
					if results_dict['result'][i]['nametype'] == agent_type and sanitizeMatchString(normalize('NFC',results_dict['result'][i]['term'])) == normalize('NFC',match_key.decode('utf-8')) and 'viafid' in results_dict['result'][i]:
						print("Found " + match_key)
						agent_uri = "http://www.viaf.org/viaf/" + results_dict['result'][i]['viafid']
						print(agent_uri)
						agent.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about',agent_uri)
						match_not_found = False
						merged_contribution_agents[match_key] = { 'agent_type': agent_type, 'uri': agent_uri }

					i = i + 1

			if match_not_found:
				merged_contribution_agents[match_key] = None
				createBlankNode(agent)
		else:
			if merged_contribution_agents[match_key] is not None:
				if merged_contribution_agents[match_key]['agent_type'] == agent_type:
					agent.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about',merged_contribution_agents[match_key]['uri'])
				else:
					createBlankNode(agent)
			else:
				createBlankNode(agent)

	print('^-CONTRIBUTION AGENT--CONTRIBUTION AGENT--CONTRIBUTION AGENT--CONTRIBUTION AGENT-^')


def postConversionTransform(file_name):
	connection = MySQLConnection(user='root',password='',database='subjects')
	cursor = connection.cursor(buffered=True)
	print(file_name)
	tree = etree.parse(file_name)
	root = tree.getroot()

	works = root.xpath('/rdf:RDF/bf:Work', namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
	print(len(works))
	print(works)

	merged_subject_agents = {}
	merged_contribution_agents = {}
	merged_topic_agents = {}
	last_loaded_worldcat_record = None

	for work in works:
		print('V-WORK--WORK--WORK--WORK--WORK--WORK--WORK--WORK--WORK--WORK--WORK--WORK--WORK--WORK-V')
		placeholder_work_id = work.xpath("./@rdf:about", namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#" })[0]
		instances = root.xpath("/rdf:RDF/bf:Instance[bf:instanceOf/@rdf:resource='" + placeholder_work_id + "']", namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
		instance_url = instances[0].xpath("@rdf:about", namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#" })[0]

		print(instance_url + '.jsonld')
		last_loaded_worldcat_record = setWorkURLs(work,instances[0],placeholder_work_id,instance_url,last_loaded_worldcat_record)

		subject_agents = work.xpath("./bf:subject/bf:Agent",namespaces={ "bf": "http://id.loc.gov/ontologies/bibframe/" })
		for agent in subject_agents:
			setSubjectAgent(agent,merged_subject_agents)

		print("Starting Topics")
		topic_agents = work.xpath("./bf:subject/*[not(self::bf:Agent or self::bf:Temporal)]",namespaces={ "bf": "http://id.loc.gov/ontologies/bibframe/" })
		print(topic_agents)
		for t_agent in topic_agents:
			setTopicAgent(t_agent,merged_topic_agents,cursor)

		print("Starting Contribution Agents")
		contribution_agents = work.xpath("./bf:contribution/bf:Contribution/bf:agent/bf:Agent",namespaces={ "bf": "http://id.loc.gov/ontologies/bibframe/" })
		print(contribution_agents)
		for c_agent in contribution_agents:
			setContributionAgent(c_agent,merged_contribution_agents)
		print('^-WORK--WORK--WORK--WORK--WORK--WORK--WORK--WORK--WORK--WORK--WORK--WORK--WORK--WORK-^')

	cursor.close()
	connection.close()

	example_agents = root.xpath(".//*[contains(@*,'example.org')]")
#	print(example_agents)
	print("Number of example.org urls converted: " + str(len(example_agents)))
	for e_a in example_agents:
		print(e_a)
		print(e_a.xpath('@*')[0])
		print(e_a.xpath('name(@*[1])'))
		print(convertFillerURI(e_a.xpath('@*')[0]))
		blank_node = convertFillerURI(e_a.xpath('@*')[0])
#		placeholder_value = e_a.xpath('@*')[0]
#		if '-' in placeholder_value:
#			blank_node = convertFillerURI(e_a.xpath('@*')[0])
#		else:
#			blank_node = '_:b' + placeholder_value[placeholder_value.rfind('/')+1:placeholder_value.rfind('#')]
#			print(blank_node)
		full_attribute_name = e_a.xpath('name(@*[1])')
		print('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}' + full_attribute_name[full_attribute_name.rfind(':')+1:])
		e_a.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}' + full_attribute_name[full_attribute_name.rfind(':')+1:],blank_node)
		print(e_a.xpath('@*')[0])

#	print(merged_subject_agents)
#	print(merged_contribution_agents)
	print("Number of unique subject agents: " + str(len(merged_subject_agents)))
	print("Number of unique contribution agents: " + str(len(merged_contribution_agents)))
	print("Number of unique topics: " + str(len(merged_topic_agents)))

	with open(file_name,'w') as outfile:
		outfile.write(etree.tostring(tree))