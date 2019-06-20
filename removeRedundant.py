# -*- coding: utf-8 -*-
import sys, os, datetime, time, codecs, glob, copy, json
from datetime import timedelta
from mysql.connector import MySQLConnection

def getFolder(read_folder_name):
	output_folder_name = 'trimmed_' + read_folder_name
	if not os.path.isdir(output_folder_name):
		os.mkdir(output_folder_name)
	return output_folder_name

def processJSONCollection(filename,cursor,connection,output_filename,os_read,os_write,os_append):
	start_time = datetime.datetime.now().time()
	with open(output_filename,os_write) as build_writefile:
		print("Created Output")

	with open(output_filename,os_append) as writefile:
		with open(filename,os_read) as readfile:
			print("Filename: " + filename)
			lines = readfile.readlines()
			for line in lines:
				print("Line: " + line)
				json_line = json.loads(line)
				found_OCLC = False
				for tag in json_line['fields']:
					if found_OCLC:
						break

					if '035' in tag:
						for subf in tag['035']['subfields']:
							if 'a' in subf and subf['a'][:7] == '(OCoLC)':
								found_OCLC = True

								found_OCLC_in_DB = False
								cursor.execute('SELECT * FROM Record WHERE oclc = "' + subf['a'][7:] + '"')
								for table in cursor:
									found_OCLC_in_DB = True

									print('Table:')
									print(table)

									if table[1] == 0:
										writefile.write(line)
										cursor.execute('UPDATE Record SET encountered = %s WHERE oclc = %s',(1,table[0]))
										connection.commit()
									else:
										print(tag['035'])
										reduced_record = { "fields": [ { "035": copy.deepcopy(tag['035']) } ], "leader": json_line['leader'] }
										for tag2 in json_line['fields']:
											found_001 = False
											found_974 = False
											if '001' in tag2:
												reduced_record["fields"].append({ "001": copy.deepcopy(tag2['001']) })
												found_001 = True
											elif '974' in tag2:
												print(tag2['974'])
												reduced_record["fields"].append({ "974": copy.deepcopy(tag2['974']) })
												found_974 = True

											if found_974 and found_001:
												break

										print('~~~~~~~~~~~~~~~~~~~~~~~')
										print(json.dumps(reduced_record))
										print('-----------------------')
										writefile.write(json.dumps(reduced_record) + '\n')

									break

								if not found_OCLC_in_DB:
									writefile.write(line)
									cursor.execute('INSERT INTO Record ( oclc, encountered ) VALUES (%s,%s)',(subf['a'][7:],1))
									connection.commit()

							if found_OCLC:
								break

#								if subf['a'][7:] in found_works:
#									print(tag['035'])
#									reduced_record = { "fields": [ { "035": copy.deepcopy(tag['035']) } ], "leader": json_line['leader'] }
#									for tag2 in json_line['fields']:
#										found_001 = False
#										found_974 = False
#										if '001' in tag2:
#											reduced_record["fields"].append({ "001": copy.deepcopy(tag2['001']) })
#											found_001 = True
#										elif '974' in tag2:
#											print(tag2['974'])
#											reduced_record["fields"].append({ "974": copy.deepcopy(tag2['974']) })
#											found_974 = True
#
#										if found_974 and found_001:
#											break

#									print('~~~~~~~~~~~~~~~~~~~~~~~')
#									print(json.dumps(reduced_record))
#									print('-----------------------')
#									writefile.write(json.dumps(reduced_record) + '\n')
#								else:
#									found_works.append(subf['a'][7:])
#									writefile.write(line)
#								break
#
#						if found_OCLC:
#							break
				if not found_OCLC:
					for tag in json_line['fields']:
						if found_OCLC:
							break
							
						if '035' in tag:
							for subf in tag['035']['subfields']:
								if 'a' in subf:
									found_OCLC = True

									found_id_in_DB = False
									cursor.execute('SELECT * FROM NonOCLC_Record WHERE id = "' + subf['a'] + '"')
									for table in cursor:
										found_id_in_DB = True

										print('Table:')
										print(table)

										if table[1] == 0:
											writefile.write(line)
											cursor.execute('UPDATE NonOCLC_Record SET encountered = %s WHERE id = %s',(1,table[0]))
											connection.commit()
										else:
											print(tag['035'])
											reduced_record = { "fields": [ { "035": copy.deepcopy(tag['035']) } ], "leader": json_line['leader'] }
											for tag2 in json_line['fields']:
												found_001 = False
												found_974 = False
												if '001' in tag2:
													reduced_record["fields"].append({ "001": copy.deepcopy(tag2['001']) })
													found_001 = True
												elif '974' in tag2:
													print(tag2['974'])
													reduced_record["fields"].append({ "974": copy.deepcopy(tag2['974']) })
													found_974 = True

												if found_974 and found_001:
													break

											print('~~~~~~~~~~~~~~~~~~~~~~~')
											print(json.dumps(reduced_record))
											print('-----------------------')
											writefile.write(json.dumps(reduced_record) + '\n')

										break

									if not found_id_in_DB:
										writefile.write(line)
										cursor.execute('INSERT INTO NonOCLC_Record ( id, encountered ) VALUES (%s,%s)',(subf['a'],1))
										connection.commit()

								if found_OCLC:
									break


	end_time = datetime.datetime.now().time()
	print("Start time: " + str(start_time))
	print("End time: " + str(end_time))
	print("Run duration: " + str(datetime.datetime.combine(datetime.date.min,end_time)-datetime.datetime.combine(datetime.date.min,start_time)))

def main():
	read_folder = sys.argv[1]
	output_folder = getFolder(read_folder)
	print(output_folder)
#	found_works = []

	if os.name == 'nt':
		SLASH = '\\'
		os_read = 'rb'
		os_write = 'wb'
		os_append = 'ab'
		read_folder += SLASH
		output_folder += SLASH
	else:
		SLASH = '/'
		os_read = 'r'
		os_write = 'w'
		os_append ='a'
		read_folder += SLASH
		output_folder += SLASH

	newest_result_file = ''
	try:
		newest_result_file = max(glob.glob(output_folder + '*'), key=os.path.getctime)
		print(newest_result_file)
		restart_file = newest_result_file
	except:
		pass

	if newest_result_file:
		waiting = True
	else:
		waiting = False

	connection = MySQLConnection(user='root',password='',database='redundant')
	cursor = connection.cursor(buffered=True)

	if len(sys.argv) > 2 and sys.argv[2] == '-restart':
		cursor.execute('TRUNCATE TABLE Record')
		connection.commit()
		cursor.execute('TRUNCATE TABLE NonOCLC_Record')
		connection.commit()

	for root, dirs, files in os.walk(read_folder):
		for f in files:
			if waiting:
				sliced_restart_file = restart_file[restart_file.rfind('/')+1:]
				print(f,sliced_restart_file)
				if f == sliced_restart_file:
					waiting = False
			
			if not waiting and f != '.DS_Store':
				processJSONCollection(read_folder + f,cursor,connection,output_folder + f,os_read,os_write,os_append)

main()