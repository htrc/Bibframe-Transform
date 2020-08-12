import os, sys, logging, csv
from lxml import etree
from xmldiff import main, actions

if os.name == 'nt':
	SLASH = '\\'
else:
	SLASH = '/'

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s [%(levelname)s] %(message)s',datefmt='%H:%M:%S')

def buildStubbyTree(out_folder,node_type,node_id):
	if node_type == 'Item':
#		try:
#			os.mkdir(out_folder + SLASH + node_type + SLASH + node_id[:node_id.find('.')])
#		except:
#			pass

		root = out_folder + SLASH + node_type + SLASH + node_id[:node_id.find('.')] + SLASH
	else:
		root = out_folder + SLASH + node_type + SLASH

	after_period = node_id[node_id.find('.')+1:]
	folder_name = ''
	for index in range(0,len(after_period),3):
		folder_name += after_period[index]

#	try:
#		os.mkdir(root + folder_name)
#	except:
#		pass

	return root + folder_name + SLASH

def compareToVirtuosoFile(bib_root,id_value,triple_value,virtuoso_folder):
	virtuoso_tree = etree.parse(buildStubbyTree(virtuoso_folder,triple_value,id_value) + id_value + '.xml')
	virtuoso_root = virtuoso_tree.getroot()

	virtuoso_nodes = virtuoso_root.xpath("/rdf:RDF/bf:" + triple_value + "/*[name()!='bf:hasInstance' and name()!='bf:adminMetadata']",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
	bib_nodes = bib_root.xpath("/rdf:RDF/bf:" + triple_value + "/*[name()!='bf:hasInstance' and name()!='bf:adminMetadata']",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })

	virtuoso_admin_nodes = virtuoso_root.xpath("/rdf:RDF/bf:" + triple_value + "/bf:adminMetadata/bf:AdminMetadata/*",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
	bib_admin_nodes = bib_root.xpath("/rdf:RDF/bf:" + triple_value + "/bf:adminMetadata/bf:AdminMetadata/*",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })

	goal = len(bib_nodes + bib_admin_nodes)
	found = 0
	for bib_node in bib_nodes:
		for virt_node in [x for x in virtuoso_nodes if x.tag == bib_node.tag]:
			differences = main.diff_trees(bib_node,virt_node)
			if len(differences) == 0:
				found += 1
				break

	for bib_admin_node in bib_admin_nodes:
		for virt_admin_node in [x for x in virtuoso_admin_nodes if x.tag == bib_admin_node.tag]:
			differences = main.diff_trees(bib_admin_node,virt_admin_node)
			if len(differences) == 0:
				found += 1
				break

	if found == goal:
		return []
	else:
		record_segment = virtuoso_root.xpath("/rdf:RDF/bf:" + triple_value,namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
		record_segment = record_segment[0]

		differences = main.diff_trees(bib_root,record_segment)
		unexpected_differences = []
		if differences:
			counter = 0
			while counter < len(differences):
#				logging.debug(differences[counter])
				if isinstance(differences[counter],actions.InsertNode):
#					logging.debug(type(differences[counter]))
					if differences[counter].tag == '{http://id.loc.gov/ontologies/bibframe/}hasInstance' or differences[counter].tag == '{http://id.loc.gov/ontologies/bibframe/}hasItem': 
						counter += 3
					else:
						unexpected_differences.append(differences[counter])
						counter += 1
				else:
					unexpected_differences.append(differences[counter])
					counter += 1

			if unexpected_differences and len(unexpected_differences) > 1:
				logging.debug(triple_value + SLASH + id_value + '.xml')
#				logging.debug(differences)
				logging.debug(unexpected_differences)

		return unexpected_differences

def processRecord(bibframe_file,virtuoso_folder,outwriter):
	logging.debug(bibframe_file)
	tree = etree.parse(bibframe_file)
	root = tree.getroot()

	work = root.xpath("/rdf:RDF/bf:Work",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
	logging.debug(work)
	work = work[0]
	work_id = work.xpath("./@rdf:about",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
	work_id = work_id[0]
#	logging.debug(work_id)
	diffs = compareToVirtuosoFile(work,work_id[work_id.rfind('/')+1:],'Work',virtuoso_folder)
	if diffs and len(diffs) > 1:
		outwriter.writerow([bibframe_file,buildStubbyTree(virtuoso_folder,'Work',instance_id[instance_id.rfind('/')+1:]) + instance_id[instance_id.rfind('/')+1:] + '.xml'])
#		outwriter.writerow([bibframe_file,virtuoso_folder + '/Work/' + work_id[work_id.rfind('/')+1:] + '.xml'])
		logging.debug(bibframe_file)

	instance = root.xpath("/rdf:RDF/bf:Instance",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
#	logging.debug(instance)
	instance = instance[0]
	instance_id = instance.xpath("./@rdf:about",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
	instance_id = instance_id[0]
#	logging.debug(instance_id)
	diffs = compareToVirtuosoFile(instance,instance_id[instance_id.rfind('/')+1:],'Instance',virtuoso_folder)
	if diffs and len(diffs) > 1:
		outwriter.writerow([bibframe_file,buildStubbyTree(virtuoso_folder,'Instance',instance_id[instance_id.rfind('/')+1:]) + instance_id[instance_id.rfind('/')+1:] + '.xml'])# virtuoso_folder + '/Instance/' + instance_id[instance_id.rfind('/')+1:] + '.xml'])
		logging.debug(bibframe_file)

	item = root.xpath("/rdf:RDF/bf:Item",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
#	logging.debug(item)
	item = item[0]
	item_id = item.xpath("./@rdf:about",namespaces={ "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bf": "http://id.loc.gov/ontologies/bibframe/" })
	item_id = item_id[0]
#	logging.debug(item_id)

def findRecordDiffs(bibframe_folder,virtuoso_folder):
	if bibframe_folder[-1:] == SLASH:
		bibframe_folder = bibframe_folder[:-1]

	if virtuoso_folder[-1:] == SLASH:
		virtuoso_folder = virtuoso_folder[:-1]

	with open('big_diffs.csv','w') as outfile:
		outwriter = csv.writer(outfile,delimiter=',')
		for root, dirs, files in os.walk(bibframe_folder):
			for name in files:
				if name[0] != '.':
#					logging.debug(name)
					processRecord(root + SLASH + name,virtuoso_folder,outwriter)

if __name__ == "__main__":
	findRecordDiffs(sys.argv[1],sys.argv[2])