import sys, os, subprocess
from lxml import etree
from collections import OrderedDict

def transformGeneratedXML(generated_xml):
	bashCommand = 'xsltproc /Users/dkudeki-admin/Documents/GitHub/Bibframe-Transform/bibframe2ef/bibframe2ef.xsl ' + xml_input_file


def generateXMLTripleForVolumes(volume_ids,tree,work,instance):
	xslt = etree.parse('/Users/dkudeki-admin/Documents/GitHub/Bibframe-Transform/bibframe2ef/bibframe2ef.xsl')
	transform = etree.XSLT(xslt)

	for volume in volume_ids:
		print(volume)
		volume_metadata = tree.xpath("bf:Item[@rdf:about = '" + volume + "']",namespaces={'bf': 'http://id.loc.gov/ontologies/bibframe/', 'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'})
		item = volume_metadata[0]
#		print(etree.tostring(volume_metadata[0]))
		instance_id = item.xpath("bf:itemOf/@rdf:resource",namespaces={'bf': 'http://id.loc.gov/ontologies/bibframe/', 'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'})[0]
		if instance['id'] != instance_id:
			print(instance_id)
			#Insert Database code here to store old instance info if needed
			instance_metadata = tree.xpath("bf:Instance[@rdf:about = '" + instance_id + "']",namespaces={'bf': 'http://id.loc.gov/ontologies/bibframe/', 'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'})

			instance['id'] = instance_id
			instance['metadata'] = instance_metadata[0]

		work_id = instance['metadata'].xpath("bf:instanceOf/@rdf:resource",namespaces={'bf': 'http://id.loc.gov/ontologies/bibframe/', 'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'})[0]
		if work['id'] != work_id:
			print(work_id)
			#Insert Database code here to store old work info if needed
			work_metadata = tree.xpath("bf:Work[@rdf:about = '" + work_id + "']",namespaces={'bf': 'http://id.loc.gov/ontologies/bibframe/', 'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'})

			work['id'] = work_id
			work['metadata'] = work_metadata[0]

		new_tree = etree.XML('<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:bf="http://id.loc.gov/ontologies/bibframe/" xmlns:bflc="http://id.loc.gov/ontologies/bflc/" xmlns:madsrdf="http://www.loc.gov/mads/rdf/v1#" xmlns:dct="http://purl.org/dc/terms/" xmlns:htrc="http://wcsa.htrc.illinois.edu/">\n  </rdf:RDF>')
		new_tree.insert(0,work['metadata'])
		new_tree.insert(1,instance['metadata'])
		new_tree.insert(2,item)
		try:
			result = transform(new_tree)
			result.write_output('/Users/dkudeki-admin/Documents/GitHub/Bibframe-Transform/bibframe2ef/results_xsl/' + volume[27:] + '.json')
		except:
			print(etree.tostring(new_tree))
			for error in transform.error_log:
				print(error.message, error.line)
			sys.exit()


def main():
	bibframe_folder = '/Users/dkudeki-admin/Documents/GitHub/Bibframe-Transform/trimmed_all_volumes_json_BIBF_records'
	instance = { 'id': None, 'metadata': None }
	work = { 'id': None, 'metadata': None }
	for root, dirs, files in os.walk(bibframe_folder):
		for f in files:
			if '.xml' in f:
				file_path = bibframe_folder + '/' + f[5:-5].replace('_segment','') + '/' + f
				print(file_path)
				tree = etree.parse(file_path)
				print(tree)
				volume_ids = tree.xpath('bf:Item/@rdf:about',namespaces={'bf': 'http://id.loc.gov/ontologies/bibframe/', 'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'})
				generateXMLTripleForVolumes(list(OrderedDict.fromkeys(volume_ids)),tree,work,instance)
				sys.exit()

main()