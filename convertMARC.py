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

def traverseFiles(rootdir):
	print(rootdir)
#	rootdir = 'sample_starting_records'
	results_folder_name = getFolder(rootdir + '_XML_records/')
	bibf_results_folder_name = getFolder(rootdir + '_BIBF_records/')

	newest_bibf_file = ''
	try:
		newest_bibf_file = max(glob.glob(bibf_results_folder_name + '*'), key=os.path.getmtime)
		print(newest_bibf_file)
		restart_file = newest_bibf_file[newest_bibf_file.find('/BIBF_')+6:-4]
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

					print("Starting output writer")
					output_writer = pymarc.XMLWriter(open(results_folder_name + SLASH + name + '.xml','wb'))
					print("Opening file")
					readFile(rootdir + SLASH + name,output_writer)
					output_writer.close()

					print("Opening output file")
					bibf_output = open(bibf_results_folder_name + SLASH + 'BIBF_' + name + '.xml','w')
					print("Running bash script")
					bashCommand = 'xsltproc marc2bibframe2/xsl/marc2bibframe2.xsl ' + results_folder_name + SLASH + name + '.xml'
					process = subprocess.call(bashCommand.split(), stdout=bibf_output)
	#				ps = subprocess.Popen(['xsltproc', 'marc2bibframe2/xsl/marc2bibframe2.xsl'], stdout=subprocess.PIPE)
	#				print("Ran first half")
	#				output = subprocess.call(['python', 'postConversionTransform.py', results_folder_name + SLASH + name + '.xml'], stdin=ps.stdout)#, stdout=bibf_output)
					print("Converted " + name)
					postConversionTransform.postConversionTransform(bibf_results_folder_name + SLASH + 'BIBF_' + name + '.xml')

					end_time = datetime.datetime.now().time()
					print("Start time: " + str(start_time))
					print("End time: " + str(end_time))
					print("Run duration: " + str(datetime.datetime.combine(datetime.date.min,end_time)-datetime.datetime.combine(datetime.date.min,start_time)))

def main():
	traverseFiles(sys.argv[1])
	
main()