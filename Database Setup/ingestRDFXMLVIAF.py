# -*- coding: utf-8 -*-
import re, sys, traceback, datetime, string
from mysql.connector import MySQLConnection
from mysql.connector import errors
from unicodedata import normalize
from lxml import etree
from datetime import timedelta
import codecs

reload(sys)
sys.setdefaultencoding('utf8')

def main():
	connection = MySQLConnection(user='root',password='',database='names',collation='utf8mb4_unicode_ci')
	cursor = connection.cursor(buffered=True)

	add_name = u'INSERT INTO stored_names (label, url, class, type) VALUES (%s, %s, %s, %s)'
	check_for_name = u'SELECT * FROM stored_names WHERE url = %s AND label = %s AND class = %s COLLATE utf8mb4_unicode_ci'

	KEY_PREDICATES = ['http://schema.org/name','http://schema.org/alternateName']
	OBJECT_TYPES = ['http://schema.org/Person','http://schema.org/Organization','http://schema.org/Event','http://schema.org/Place']
	DATABASE_OBJECT_TYPES = ['personal','corporate','corporate','corporate']
	AUTHORIZED_LABEL = 'skos:prefLabel'
	VARIANT_LABEL = 'skos:altLabel'

	starting_line = 0
	durations = []

	try:
		with open('viaf_index.txt','r') as infile:
			starting_line = int(infile.readline())
	except:
		pass

	print(starting_line)

	with codecs.open('viaf-20180605-clusters-rdf.xml','r',encoding='utf-8') as readfile:
		line_counter = 0
		start_time = datetime.datetime.now().time()

		try:
			for line in readfile:
				if line_counter >= starting_line:
					sections = line.split('\t')
					url = 'http://viaf.org/viaf/' + sections[0]
					authorized_labels = []
					variant_labels = []
					record_type = None

					root = etree.fromstring(sections[1])

					discrete_descriptions = root.xpath("/rdf:RDF/rdf:Description[rdf:type/@rdf:resource='http://www.w3.org/2004/02/skos/core#Concept']", namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#" })

					for description in discrete_descriptions:
						authorized_labels.extend(description.xpath("./" + AUTHORIZED_LABEL + "/text()", namespaces={ "skos": "http://www.w3.org/2004/02/skos/core#" }))
						variant_labels.extend(description.xpath("./" + VARIANT_LABEL + "/text()", namespaces={ "skos": "http://www.w3.org/2004/02/skos/core#" }))

					authorized_labels = list(map(lambda x: unicode(x).strip(string.whitespace), authorized_labels))
					authorized_labels = list(map(lambda x: x[:200] if len(x) > 200 else x, authorized_labels))
					authorized_labels = list(set(authorized_labels))
					variant_labels = list(map(lambda x: unicode(x).strip(string.whitespace), variant_labels))
					variant_labels = list(map(lambda x: x[:200] if len(x) > 200 else x, variant_labels))
					variant_labels = list(set(variant_labels))

					index = 0
					while record_type is None and index < len(OBJECT_TYPES):
						type_results = root.xpath("/rdf:RDF/rdf:Description[rdf:type/@rdf:resource='" + OBJECT_TYPES[index] + "']", namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#" })
						if len(type_results) > 0:
							record_type = DATABASE_OBJECT_TYPES[index]
						index = index + 1

					for l in authorized_labels:
						cursor.execute(add_name,(l,url,'authorized',record_type))
						connection.commit()

					for m in variant_labels:
						cursor.execute(add_name,(m,url,'variant',record_type))
						connection.commit()
#					first_index = line.find('>')
#					first_component = line[:first_index+1]
#
#					if first_component[:16] == '<http://viaf.org':
#						second_substring = line[first_index+2:]
#						second_index = second_substring.find('>')
#						second_component = second_substring[:second_index+1]
#
#						if second_component in KEY_PREDICATES:
#							third_component = second_substring[second_index+2:-3]
#							if '@' in third_component and third_component.rfind('@') > third_component.rfind('"'):
#								third_component = third_component[1:third_component.rfind('@')-1]
#							elif second_component == KEY_PREDICATES[1] or (third_component[:1] == '"' and third_component[-1:] == '"'):
#								third_component = third_component[1:-1]
#
#							if KEY_PREDICATES[0] == second_component:
#								name_class = 0
#							else:
#								name_class = 1
#
#							first_component = first_component[1:-1]
#							second_component = second_component[1:-1]
#							third_component = third_component.decode('unicode_escape')
#
#							if len(third_component) <= 200 and len(first_component) <= 200:
#								print(first_component)
#								print(second_component)
#								print(third_component)
#
#								cursor.execute(check_for_name,(first_component,third_component,name_class))
#								if not cursor.rowcount:
#									cursor.execute(add_name,(first_component,third_component,name_class))
#									connection.commit()

				line_counter = line_counter + 1
				if line_counter % 1000 == 0 and line_counter >= starting_line:
					print(line_counter)
					end_time = datetime.datetime.now().time()
					duration = datetime.datetime.combine(datetime.date.min,end_time)-datetime.datetime.combine(datetime.date.min,start_time)
					if duration >= timedelta(0):
						durations.append(duration)
					print("Run duration: " + str(duration))
					average = reduce(lambda x, y: x + y, durations) / len(durations)
					print("Estimated average: " + str(average))
					print("Estimated remining time: " + str(average * (211 - (line_counter/1000))))
					start_time = end_time
		except (KeyboardInterrupt, errors.DataError, errors.DatabaseError, UnicodeDecodeError) as e:
			with open('viaf_index.txt','w') as outfile:
				outfile.write(str(line_counter))
				traceback.print_exc()
#				raise TypeError(e)

	cursor.close()
	connection.close()

main()