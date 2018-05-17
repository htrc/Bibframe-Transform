# -*- coding: utf-8 -*-
import re, sys, traceback, datetime
from mysql.connector import MySQLConnection
from mysql.connector import errors
from unicodedata import normalize
from datetime import timedelta
import codecs

reload(sys)
sys.setdefaultencoding('utf8')

def main():
	connection = MySQLConnection(user='root',password='',database='names')
	cursor = connection.cursor(buffered=True)

	update_type = u'UPDATE names SET type = %s WHERE url = %s AND type IS NULL'

	object_types = ['<http://schema.org/Person>','<http://schema.org/Organization>','<http://schema.org/Event>']
	durations = []

	starting_line = 0
	try:
		with open('viaf_index.txt','r') as infile:
			starting_line = int(infile.readline())
	except:
		pass

	print(starting_line)

	with open('viaf-20180429-clusters-rdf.nt','r') as readfile:
		line_counter = 0
		start_time = datetime.datetime.now().time()

		try:
			for line in readfile:
				if line_counter >= starting_line:
					first_index = line.find('>')
					first_component = line[:first_index+1]

					if first_component[:16] == '<http://viaf.org':
						second_substring = line[first_index+2:]
						second_index = second_substring.find('>')
						second_component = second_substring[:second_index+1]

						if second_component == '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>':
							third_component = second_substring[second_index+2:-3]

							if third_component in object_types:
								object_type = None
								if third_component == object_types[0]:
									object_type = 'personal'
								else:
									object_type = 'corporate'

								first_component = first_component[1:-1]

								if line_counter == starting_line:
									print((object_type,first_component))

								try:
									cursor.execute(update_type,(object_type,first_component))
								except errors.DatabaseError:
									pass


				line_counter = line_counter + 1
				if line_counter % 1000000 == 0 and line_counter >= starting_line:
					print(line_counter)
					end_time = datetime.datetime.now().time()
					duration = datetime.datetime.combine(datetime.date.min,end_time)-datetime.datetime.combine(datetime.date.min,start_time)
					durations.append(duration)
					print("Run duration: " + str(duration))
					average = reduce(lambda x, y: x + y, durations) / len(durations)
					print("Estimated average: " + str(average))
					print("Estimated remining time: " + str(average * (728 - (line_counter/1000000))))
					start_time = end_time
		except (KeyboardInterrupt, errors.DataError, errors.DatabaseError, UnicodeDecodeError) as e:
			with open('viaf_index.txt','w') as outfile:
				outfile.write(str(line_counter))
				traceback.print_exc()
#				raise TypeError(e)

	cursor.close()
	connection.close()

main()