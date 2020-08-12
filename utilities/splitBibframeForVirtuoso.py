import os, sys, logging, re
from lxml import etree
from xmldiff import main, actions

if os.name == 'nt':
	SLASH = '\\'
else:
	SLASH = '/'

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s [%(levelname)s] %(message)s',datefmt='%H:%M:%S')

def getFolder(read_folder_name):
    output_folder_name = read_folder_name
    if not os.path.isdir(output_folder_name):
        os.mkdir(output_folder_name)
        os.mkdir(output_folder_name + SLASH + 'Work')
        os.mkdir(output_folder_name + SLASH + 'Instance')
        os.mkdir(output_folder_name + SLASH + 'Item')
    return output_folder_name

def removeDuplicateURLs(prospective_additions,extant_links):
	output = []
	for node in prospective_additions:
		if node.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource'] not in extant_links:
			output.append(node)
#		print(node.xpath("@rdf:hasInstance",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" }))
#	print(extant_links)
	return output

#def mergeNewAndSaved(new_nodes,saved_root,saved_node_path):
#	nsmapping = { 'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf', 'http://id.loc.gov/ontologies/bibframe/': 'bf', 'http://www.w3.org/2000/01/rdf-schema#': 'rdfs' }
#	for node in new_nodes:
#		node_name = etree.QName(node)
#		found_nodes = saved_root.xpath(saved_node_path + nsmapping[node_name.namespace] + ':' + node_name.localname,namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/", "rdfs": "http://www.w3.org/2000/01/rdf-schema#" })
#		if len(found_nodes) == 0:

def mergeNewAndSaved(new_nodes,saved_nodes,modifying_node):
	for node in new_nodes:
		if node.tag not in [ t.tag for t in saved_nodes ]:
			modifying_node.append(node)
		else:
			found = False
			for saved_node in [ x for x in saved_nodes if x.tag == node.tag ]:
				differences = main.diff_trees(node,saved_node)
				if len(differences) == 0:
					found = True
					break

			if not found:
				modifying_node.append(node)

#	print(" ")
#	for sn in saved_nodes:
#		print(sn)
#	nsmapping = { 'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf', 'http://id.loc.gov/ontologies/bibframe/': 'bf', 'http://www.w3.org/2000/01/rdf-schema#': 'rdfs' }
#	for node in new_nodes:
#		node_name = etree.QName(node)
#		found_nodes = saved_root.xpath(saved_node_path + nsmapping[node_name.namespace] + ':' + node_name.localname,namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/", "rdfs": "http://www.w3.org/2000/01/rdf-schema#" })
#		if len(found_nodes) == 0:

def mergeWorks(new_root,saved_root):
	new_nodes = new_root.xpath("/rdf:RDF/bf:Work/*[name()!='bf:hasInstance' and name()!='bf:adminMetadata']",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
#	mergeNewAndSaved(new_nodes,saved_root,"/rdf:RDF/bf:Work/")
	modifying_node = saved_root.xpath("/rdf:RDF/bf:Work",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
	modifying_node = modifying_node[0]
	saved_nodes = modifying_node.xpath("*[name()!='bf:hasInstance' and name()!='bf:adminMetadata']",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
	mergeNewAndSaved(new_nodes,saved_nodes,modifying_node)
	new_admin_node = new_root.xpath("/rdf:RDF/bf:Work/bf:adminMetadata/bf:AdminMetadata/*",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
	modifying_admin_node = saved_root.xpath("/rdf:RDF/bf:Work/bf:adminMetadata/bf:AdminMetadata",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
	modifying_admin_node = modifying_admin_node[0]
	saved_admin_nodes = modifying_admin_node.xpath("*",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
	mergeNewAndSaved(new_admin_node,saved_admin_nodes,modifying_admin_node)

def mergeInstances(new_root,saved_root):
	new_nodes = new_root.xpath("/rdf:RDF/bf:Instance/*[name()!='bf:hasItem']",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
	modifying_node = saved_root.xpath("/rdf:RDF/bf:Instance",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
	modifying_node = modifying_node[0]
	saved_nodes = modifying_node.xpath("*[name()!='bf:hasItem']",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
	mergeNewAndSaved(new_nodes,saved_nodes,modifying_node)

def buildStubbyTree(out_folder,node_type,node_id):
	if node_type == 'Item':
		try:
			os.mkdir(out_folder + SLASH + node_type + SLASH + node_id[:node_id.find('.')])
		except:
			pass

		root = out_folder + SLASH + node_type + SLASH + node_id[:node_id.find('.')] + SLASH
	else:
		root = out_folder + SLASH + node_type + SLASH

	after_period = node_id[node_id.find('.')+1:]
	folder_name = ''
	for index in range(0,len(after_period),3):
		folder_name += after_period[index]

	try:
		os.mkdir(root + folder_name)
	except:
		pass

	return root + folder_name + SLASH

def prepareForBulkUpload(out_folder,node_id):
	generated_folder = out_folder + node_id + SLASH
	try:
		os.mkdir(generated_folder)
	except:
		pass

	with open(generated_folder + node_id + '.xml.graph','w') as graph_file:
		graph_file.write('http://localhost:8890/DAV/')

	return generated_folder

def createOrModifyNodeFile(root,node_type,out_folder):
	node_id = root.xpath("/rdf:RDF/bf:" + node_type + "/@rdf:about",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
	node_id = node_id[0][node_id[0].rfind('/')+1:]
	node = root.xpath("/rdf:RDF/bf:" + node_type,namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })

	stubby_out_folder = buildStubbyTree(out_folder,node_type,node_id)
	stubby_out_folder = prepareForBulkUpload(stubby_out_folder,node_id)

	if not os.path.isfile(stubby_out_folder + node_id + '.xml'):
		#Create
		#Isolate Work and write results to this folder, possibly removing the bf:hasInstance property
		NSMAP = { "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdfs": "http://www.w3.org/2000/01/rdf-schema#", "bf": "http://id.loc.gov/ontologies/bibframe/", "bflc": "http://id.loc.gov/ontologies/bflc/", "madsrdf": "http://www.loc.gov/mads/rdf/v1#", "dct": "http://purl.org/dc/terms/", "htrc": "http://wcsa.htrc.illinois.edu/" }
		rdf_root = etree.Element('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF', nsmap=NSMAP)
		rdf_root.append(node[0])

		with open(stubby_out_folder + node_id + '.xml','w') as outfile:
			outfile.write(etree.tostring(rdf_root))

	else:
		#modify
		if node_type == 'Work':
			links = root.xpath("/rdf:RDF/bf:Work/*[name()='bf:hasInstance' and @rdf:resource]",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
		else:
			links = root.xpath("/rdf:RDF/bf:Instance/*[name()='bf:hasItem' and @rdf:resource]",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })

		tree = etree.parse(stubby_out_folder + node_id + '.xml')
		modifying_root = tree.getroot()
		modifying_node = modifying_root.xpath("/rdf:RDF/bf:" + node_type,namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
		modifying_node = modifying_node[0]

		if node_type == 'Work':
			mergeWorks(root,modifying_root)
			links = removeDuplicateURLs(links,modifying_node.xpath("bf:hasInstance/@rdf:resource",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" }))
		elif node_type == 'Instance':
			mergeInstances(root,modifying_root)

		logging.debug(stubby_out_folder + node_id + '.xml')
		for link in links:
			modifying_node.append(link)
#			logging.debug(link)
#			logging.debug(etree.tostring(modifying_node,pretty_print=True))

#		print(etree.tostring(link,pretty_print=True))

		with open(stubby_out_folder + node_id + '.xml','w') as outfile:
			outfile.write(etree.tostring(modifying_root))
#			outfile.write(re.sub(r'>\s+<','><',etree.tostring(modifying_root)))

#def addLinks(out_folder,filename,links):
#	tree = etree.parse(out_folder + SLASH + filename)
#	root = tree.getroot()

def processSingleVolumeFile(input_folder,filename,out_folder):
	tree = etree.parse(input_folder + SLASH + filename)
	root = tree.getroot()
	createOrModifyNodeFile(root,'Work',out_folder)
	createOrModifyNodeFile(root,'Instance',out_folder)

	print(filename)
#	work_non_connecting_nodes = root.xpath("/rdf:RDF/bf:Work/*[name()='bf:hasInstance' and @rdf:resource]",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
#	print(work_non_connecting_nodes)
#	for w_node in work_non_connecting_nodes:
#		w_node.getparent().remove(w_node)

#	instance_non_connecting_nodes = root.xpath("/rdf:RDF/bf:Instance/*[name()='bf:hasItem' or name()='bf:instanceOf' and @rdf:resource]",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
#	print(instance_non_connecting_nodes)
#	for i_node in instance_non_connecting_nodes:
#		i_node.getparent().remove(i_node)

	work = root.xpath("/rdf:RDF/bf:Work",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
#	print(work)
	if work:
		root.remove(work[0])
	instance = root.xpath("/rdf:RDF/bf:Instance",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
#	print(instance)
	if instance:
		root.remove(instance[0])

	stubby_out_folder = buildStubbyTree(out_folder,'Item',filename[:-4])
	stubby_out_folder = prepareForBulkUpload(stubby_out_folder,filename[:-4])
	with open(stubby_out_folder + filename,'w') as outfile:
		outfile.write(etree.tostring(root))

#This script splits single-record BIBFRAME XML files into XML files for their Work, Instance and Item components.
#If there is already a file for the Work or Instance the appropriate hasInstance or hasItem fields are added to the existing file.
def splitBibframeForVirtuoso(input_folder,output_folder):
	if input_folder[-1:] == SLASH:
		input_folder = input_folder[:-1]

	if output_folder[-1:] == SLASH:
		output_folder = output_folder[:-1]	

	out_folder = getFolder(output_folder)

	for root, dirs, files in os.walk(input_folder):
		for name in files:
			if name[0] != '.':
				processSingleVolumeFile(root,name,output_folder)

if __name__ == "__main__":
	splitBibframeForVirtuoso(sys.argv[1],sys.argv[2])