import re, sys
from mysql.connector import MySQLConnection

def main():
	connection = MySQLConnection(user='root',password='',database='subjects')
	cursor = connection.cursor(buffered=True)

	add_subject = u'INSERT INTO Subject (url, label, concept_type) VALUES (%s, %s, %s)'
	add_component = u'INSERT INTO Component (source_url, sequence_value, component_url) VALUES (%s, %s, %s)'
	add_variant_name = u'INSERT INTO Variant_Name (url, variant_name) VALUES (%s, %s)'

	subjects = {}

	ignorable_topics = ['<http://www.loc.gov/mads/rdf/v1#Authority>', '<http://www.loc.gov/mads/rdf/v1#DeprecatedAuthority>', '<http://www.loc.gov/mads/rdf/v1#Variant>']

	with open('authoritiessubjects.madsrdf.ttl','r') as readfile:
		working_object = {}
		subject_url = ''
		component_list = []
		variant_list = []
		getting_components = False
		getting_variants = False
		for line in readfile:
			if getting_components:
				if line.find('    ) ;') == 0:
					getting_components = False
					working_object['component_list'] = component_list
				else:
					pattern = re.compile('<http://id.loc.gov/authorities/[a-zA-Z0-9.//]*>')
					matches = pattern.findall(line)
					if matches:
						component_list.append(matches[0][1:-1])
			elif getting_variants:
				if line.find('    ] ;') == 0:
					getting_variants = False
					print(variant_list)
					working_object['variant_list'] = list(set(variant_list))
					print(working_object['variant_list'])
				else:
					if '<http://www.loc.gov/mads/rdf/v1#variantLabel>' in line:
						pattern = re.compile('".*"')
						matches = pattern.findall(line)
						if matches:
							variant_list.append(matches[0][1:-1])
			elif line.find('<http://id.loc.gov/authorities/') == 0:
				subjects[subject_url] = working_object
				#Add the last subject to the dictionary of subjects

#				print(working_object)
				print(subject_url)

				label = None
				if 'label' in working_object:
					label = working_object['label']

				topics = None
				if 'topics' in working_object:
					topics = working_object['topics']

				subject_data = (subject_url,label,topics)
				cursor.execute(add_subject,subject_data)
				connection.commit()

				if 'component_list' in working_object:
					iterator = 0
					while iterator < len(working_object['component_list']):
						component_data = (subject_url,iterator,working_object['component_list'][iterator])
						cursor.execute(add_component,component_data)
						connection.commit()
						iterator = iterator + 1

				if 'variant_list' in working_object:
					for variant in working_object['variant_list']:
						print(variant)
						variant_data = (subject_url,variant)
						cursor.execute(add_variant_name,variant_data)
						connection.commit()

				#Start buildign a new subject
				subject_url = line[1:-2]
				working_object = {}
				component_list = []
				variant_list = []
			elif line.find('    a') == 0:
				pattern = re.compile('<[a-zA-Z0-9.//#:]*>')
				matches = pattern.findall(line)
				good_match = ''
				for match in matches:
					if match not in ignorable_topics:
						if good_match == '' or good_match == 'http://www.loc.gov/mads/rdf/v1#ComplexSubject':
							good_match = match[1:-1]

				working_object['topics'] = good_match
			elif line.find('    <http://www.loc.gov/mads/rdf/v1#authoritativeLabel>') == 0:
				pattern = re.compile('".*"')
				matches = pattern.findall(line)
				working_object['label'] = matches[0][1:-1]
			elif line.find('    <http://www.loc.gov/mads/rdf/v1#componentList>') == 0:
				getting_components = True
				pattern = re.compile('<http://id.loc.gov/authorities/[a-zA-Z0-9.//]*>')
				matches = pattern.findall(line[line.find('('):])
				if matches:
					component_list.append(matches[0][1:-1])
			elif line.find('    <http://www.loc.gov/mads/rdf/v1#hasVariant>') == 0:
				getting_variants = True
				if '<http://www.loc.gov/mads/rdf/v1#variantLabel>' in line:
					pattern = re.compile('".*"')
					matches = pattern.findall(line)
					if matches:
						variant_list.append(matches[0][1:-1])

	print(subjects)
	cursor.close()
	connection.close()

main()