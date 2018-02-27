import pymarc, os, subprocess, time, datetime
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

def traverseFiles():
	rootdir = 'sample_starting_records'
	results_folder, results_folder_name = makeOutputFolder('XML_records',None)
	bibf_results_folder, bibf_results_folder_name = makeOutputFolder('BIBF_records',None)

	for root, dirs, files in os.walk(rootdir):
		for name in files:
			if name[0] != '.':
				print("Starting output writer")
				output_writer = pymarc.XMLWriter(open(results_folder_name + SLASH + name[:name.rfind('.')] + '.xml','wb'))
				print("Opening file")
				readFile(rootdir + SLASH + name,output_writer)
				output_writer.close()

				print("Opening output file")
				bibf_output = open(bibf_results_folder_name + SLASH + 'BIBF_' + name[:name.rfind('.')] + '.xml','w')
				print("Running bash script")
				bashCommand = 'xsltproc marc2bibframe2/xsl/marc2bibframe2.xsl ' + results_folder_name + SLASH + name[:name.rfind('.')] + '.xml'
				process = subprocess.call(bashCommand.split(), stdout=bibf_output)
#				ps = subprocess.Popen(['xsltproc', 'marc2bibframe2/xsl/marc2bibframe2.xsl'], stdout=subprocess.PIPE)
#				print("Ran first half")
#				output = subprocess.call(['python', 'postConversionTransform.py', results_folder_name + SLASH + name[:name.rfind('.')] + '.xml'], stdin=ps.stdout)#, stdout=bibf_output)
				print("Converted " + name)
				postConversionTransform.postConversionTransform(bibf_results_folder_name + SLASH + 'BIBF_' + name[:name.rfind('.')] + '.xml')

def main():
	start_time = datetime.datetime.now().time()
	traverseFiles()
	end_time = datetime.datetime.now().time()
	print("Start time: " + str(start_time))
	print("End time: " + str(end_time))
	print("Run duration: " + str(datetime.datetime.combine(datetime.date.min,end_time)-datetime.datetime.combine(datetime.date.min,start_time)))

main()