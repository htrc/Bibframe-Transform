# -*- coding: utf-8 -*-
import re, sys, traceback
from mysql.connector import MySQLConnection
from mysql.connector import errors
from unicodedata import normalize
import codecs

reload(sys)
sys.setdefaultencoding('utf8')

def main():
	connection = MySQLConnection(user='root',password='',database='names',collation='utf8mb4_unicode_ci')
	cursor = connection.cursor(buffered=True)

	add_name = u'INSERT INTO names (url, label, class) VALUES (%s, %s, %s)'
	check_for_name = u'SELECT * FROM names WHERE url = %s AND label = %s AND class = %s COLLATE utf8mb4_unicode_ci'

	key_predicates = ['<http://schema.org/name>','<http://schema.org/alternateName>']

	starting_line = 0
	try:
		with open('viaf_index.txt','r') as infile:
			starting_line = int(infile.readline())
	except:
		pass

	print(starting_line)

	with open('viaf-20180429-clusters-rdf.nt','r') as readfile:
		line_counter = 0

		try:
			for line in readfile:
				if line_counter >= starting_line:
					first_index = line.find('>')
					first_component = line[:first_index+1]

					if first_component[:16] == '<http://viaf.org':
						second_substring = line[first_index+2:]
						second_index = second_substring.find('>')
						second_component = second_substring[:second_index+1]

						if second_component in key_predicates:
							third_component = second_substring[second_index+2:-3]
							if '@' in third_component and third_component.rfind('@') > third_component.rfind('"'):
								third_component = third_component[1:third_component.rfind('@')-1]
							elif second_component == key_predicates[1] or (third_component[:1] == '"' and third_component[-1:] == '"'):
								third_component = third_component[1:-1]

							if key_predicates[0] == second_component:
								name_class = 0
							else:
								name_class = 1

							first_component = first_component[1:-1]
							second_component = second_component[1:-1]
							third_component = third_component.decode('unicode_escape')

							if len(third_component) <= 200 and len(first_component) <= 200:
								print(first_component)
								print(second_component)
								print(third_component)

								cursor.execute(check_for_name,(first_component,third_component,name_class))
								if not cursor.rowcount:
									cursor.execute(add_name,(first_component,third_component,name_class))
									connection.commit()

				line_counter = line_counter + 1
		except (KeyboardInterrupt, errors.DataError, errors.DatabaseError, UnicodeDecodeError) as e:
			with open('viaf_index.txt','w') as outfile:
				outfile.write(str(line_counter))
				traceback.print_exc()
#				raise TypeError(e)

	cursor.close()
	connection.close()

main()