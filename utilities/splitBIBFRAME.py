import sys, os, logging
from lxml import etree

if os.name == 'nt':
	SLASH = '\\'
else:
	SLASH = '/'

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s [%(levelname)s] %(message)s',datefmt='%H:%M:%S')

def getFolder(read_folder_name):
    output_folder_name = read_folder_name
    if not os.path.isdir(output_folder_name):
        os.mkdir(output_folder_name)
    return output_folder_name

def buildStubbyTree(out_folder,item_id):
	try:
		os.mkdir(out_folder + SLASH + item_id[:item_id.find('.')])
	except:
		pass

	root = out_folder + SLASH + item_id[:item_id.find('.')] + SLASH

	after_period = item_id[item_id.find('.')+1:]
	folder_name = ''
	for index in range(0,len(after_period),3):
		folder_name += after_period[index]

	try:
		os.mkdir(root + folder_name)
	except:
		pass

	return root + folder_name + SLASH

def buildNewBIBFRAMEFile(bibf_record,output_folder):
	NSMAP = { "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdfs": "http://www.w3.org/2000/01/rdf-schema#", "bf": "http://id.loc.gov/ontologies/bibframe/", "bflc": "http://id.loc.gov/ontologies/bflc/", "madsrdf": "http://www.loc.gov/mads/rdf/v1#", "dct": "http://purl.org/dc/terms/", "htrc": "http://wcsa.htrc.illinois.edu/" }
	rdf_root = etree.Element('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF', nsmap=NSMAP)
	for segment in bibf_record:
		rdf_root.append(segment)

	item_id = rdf_root.xpath('/rdf:RDF/bf:Item/@rdf:about', namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
	with open(buildStubbyTree(output_folder,item_id[0][27:]) + item_id[0][27:] + '.xml','w') as outfile:
		outfile.write(etree.tostring(rdf_root,pretty_print=True))

def splitXML(xml_file,output_folder):
	tree = etree.parse(xml_file)
	root = tree.getroot()
	children = root.xpath('/rdf:RDF/child::node()[. != "\n  " and . != "\n"]', namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#" })
	
	index = 0
	index_end = len(children)

	while index < index_end:
		bibf_record = []
		bibf_record.append(children[index])
		bibf_record.append(children[index+1])

		counter = 2

		logging.debug(children[index])
		logging.debug(children[index+1])
		while index + counter < index_end and children[index + counter].tag == '{http://id.loc.gov/ontologies/bibframe/}Item':
			bibf_record.append(children[index + counter])
			counter += 1


		buildNewBIBFRAMEFile(bibf_record,output_folder)

		index = index + counter

#This script is used to split large XML files that contain multiple records into multiple single-record XML files to match what Boris is producing
def splitBIBFRAME(input_folder):
	logging.debug(input_folder)
	if input_folder[-1:] == SLASH:
		input_folder = input_folder[:-1]

	output_folder = getFolder(input_folder + '_split/')

	for root, dirs, files in os.walk(input_folder):
		for name in files:
			if name[0] != '.':
				splitXML(root + SLASH + name,output_folder)

if __name__ == "__main__":
	splitBIBFRAME(sys.argv[1])