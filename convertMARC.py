import pymarc, os, subprocess, time, datetime, sys, glob
import postConversionTransform
from datetime import timedelta

if os.name == 'nt':
	SLASH = '\\'
else:
	SLASH = '/'

def convertJSONToMARCXML(JSON_record,output_writer):
	as_json_reader = pymarc.JSONReader(JSON_record)
	for record_object in as_json_reader:
		output_writer.write(record_object)
#	record_object = next(as_json_reader)
#	print(record_object)
#	print(as_pymarc)
#	output_writer.write(as_pymarc)

def readFile(filename,output_writer):
	print(filename)
	with open(filename,'r') as read_file:
		for line in read_file:
			convertJSONToMARCXML(line,output_writer)

def getFolder(read_folder_name):
    output_folder_name = read_folder_name
    if not os.path.isdir(output_folder_name):
        os.mkdir(output_folder_name)
    return output_folder_name

def makeOutputFolder(folder_name,counter):
	try:
		if counter is not None:
			write_folder_name = folder_name + '_' + str(counter)
		else:
			write_folder_name = folder_name

		write_folder = os.mkdir(write_folder_name)
		return write_folder, write_folder_name
	except OSError:
		if counter is not None:
			return makeOutputFolder(folder_name,counter+1)
		else:
			return makeOutputFolder(folder_name,0)

#	rootdir is either a folder containing JSON files to be converted or XML files to be converted
def traverseFiles(rootdir):
	print(rootdir)
#	rootdir = 'sample_starting_records'

	read_format = 'json'
	if len(sys.argv) > 2 and sys.argv[2] == '-xml':
		results_folder_name = rootdir
		read_format = 'xml'
	else:
		results_folder_name = getFolder(rootdir + '_XML_records/')

	bibf_results_folder_name = getFolder(rootdir + '_BIBF_records/')

	# If the process was stopped prematurely, we want to restart based on the last file that was being worked on
	newest_bibf_file = ''
	try:
		newest_bibf_file = max(glob.glob(bibf_results_folder_name + '*.xml'), key=os.path.getmtime)
		print(newest_bibf_file)
		if read_format == 'json':
			restart_file = newest_bibf_file[newest_bibf_file.find('/BIBF_')+6:-4]
		else:
			restart_file = newest_bibf_file[newest_bibf_file.find('/BIBF_')+6:]
	except:
		pass

	if newest_bibf_file:
		waiting = True
	else:
		waiting = False

	for root, dirs, files in os.walk(rootdir):
		for name in files:
			if waiting:
				print(name,restart_file)
				if name == restart_file:
					waiting = False

			if not waiting:		
				if name[0] != '.':
					start_time = datetime.datetime.now().time()

					print(read_format)
					# Convert JSON files into MARCXML
					if read_format == 'json':
						print("Starting output writer")
						output_writer = pymarc.XMLWriter(open(results_folder_name + SLASH + name + '.xml','wb'))
						print("Opening file")
						readFile(rootdir + SLASH + name,output_writer)
						output_writer.close()

					print("Opening output file")
					# Convert MARCXML into BIBFRAME
					if read_format == 'json':
						bibf_output_file = bibf_results_folder_name + SLASH + 'BIBF_' + name + '.xml'
						xml_input_file = results_folder_name + SLASH + name + '.xml'
					else:
						bibf_output_file = bibf_results_folder_name + SLASH + 'BIBF_' + name
						xml_input_file = root + SLASH + name
						print(xml_input_file)

					bibf_output = open(bibf_output_file,'w')
					print("Running bash script")
					bashCommand = 'xsltproc marc2bibframe2/xsl/marc2bibframe2.xsl ' + xml_input_file
					process = subprocess.call(bashCommand.split(), stdout=bibf_output)

					print("Converted " + name)
					# Enchance converted BIBFRAME by adding Linked Data URLs
					postConversionTransform.postConversionTransform(bibf_output_file)

					end_time = datetime.datetime.now().time()
					print("Start time: " + str(start_time))
					print("End time: " + str(end_time))
					print("Run duration: " + str(datetime.datetime.combine(datetime.date.min,end_time)-datetime.datetime.combine(datetime.date.min,start_time)))

def main():
	traverseFiles(sys.argv[1])
	
main()