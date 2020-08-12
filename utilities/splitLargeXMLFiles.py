import os, sys, math

def generateNewFiles(filename,divisions,output_folder):
	output_file_name = output_folder + 'new_' + filename[filename.rfind('/')+1:-4] + '_'
	print(output_file_name)

	first_line = '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:bf="http://id.loc.gov/ontologies/bibframe/" xmlns:bflc="http://id.loc.gov/ontologies/bflc/" xmlns:madsrdf="http://www.loc.gov/mads/rdf/v1#" xmlns:dct="http://purl.org/dc/terms/" xmlns:htrc="http://wcsa.htrc.illinois.edu/">\n'
	last_line = '</rdf:RDF>'

	with open(filename,'r') as read_file:
		for i, l in enumerate(read_file):
			pass
		line_count = i+1
		minimum_new_file_line_count = line_count/divisions

		read_file.seek(0)
		line = read_file.readline()
		count = 1
		out_count = 1
		split_count = 1

		out_file = open(output_file_name + str(split_count) + '.xml','w')
		out_file.write(first_line)

		while line:
			if count != 1 and count != line_count:
				out_file.write(line)

				if out_count >= minimum_new_file_line_count and line == '  </bf:Item>\n':
					out_file.write(last_line)
					out_file.close()

					out_count = 0
					split_count += 1

					out_file = open(output_file_name + str(split_count) + '.xml','w')
					out_file.write(first_line)

				out_count += 1

			line = read_file.readline()
			count += 1

		out_file.write(last_line)
		out_file.close

		print(line)

def splitLargeXMLFiles(input_folder,output_folder):
	for root, dirs, files in os.walk(input_folder):
		for f in files:
			size_mb = os.path.getsize(root + f) / 1024 / 1024
			if size_mb >= 70:
				divisions = int(math.ceil(size_mb/30.0))
				generateNewFiles(root + f,divisions,output_folder)
			else:
				os.rename(input_folder + f,output_folder + f)

splitLargeXMLFiles(sys.argv[1],sys.argv[2])