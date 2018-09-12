var fs = require("fs");
var async = require('async');

function buildSolrJSON(handle,revised) {
	console.log(JSON.stringify(revised));
	var solr_json = {};
	solr_json['title'] = revised['metadata']['title'];
	solr_json['id'] = revised['metadata']['id'];
	solr_json['type'] = revised['metadata']['type'];
	if ('contributor' in revised['metadata']) {
		if (revised['metadata']['contributor'] instanceof Array) {
			var creators = [];
			for (var i = 0; i < revised['metadata']['contributor'][i].length; i++) {
				if (revised['metadata']['contributor'][i]['name'] instanceof Array) {
					creators.push(revised['metadata']['contributor'][i]['name'][0]);
				}
				else {
					creators.push(revised['metadata']['contributor'][i]['name']);
				}
			}
			solr_json['contributor'] = creators;
		}
		else {
			if (revised['metadata']['contributor']['name'] instanceof Array) {
				solr_json['contributor'] = revised['metadata']['contributor']['name'][0];
			}
			else {
				solr_json['contributor'] = revised['metadata']['contributor']['name'];
			}
		}
	}
	solr_json['provider'] = 'htrc';

	if ('issn' in revised['metadata']) {
		solr_json['issn'] = revised['metadata']['issn'];
	}

	if ('isPartOf' in revised['metadata']) {
		if (revised['metadata']['isPartOf']['title'] instanceof Array) {
			solr_json['journalTitle'] = revised['metadata']['isPartOf']['title'][0];
		}
		else {
			solr_json['journalTitle'] = revised['metadata']['isPartOf']['title'];
		}
	}

	if ('genre' in revised['metadata']) {
		solr_json['genre'] = revised['metadata']['genre'];
	}

	if ('typeOfResource' in revised['metadata']) {
		solr_json['typeOfResource'] = revised['metadata']['typeOfResource'];
	}

	if ('isAccessibleForFree' in revised['metadata']) {
		solr_json['isAccessibleForFree'] = revised['metadata']['isAccessibleForFree'];
	}

	if ('rightsAttributes' in revised['metadata']) {
		if (revised['metadata']['rightsAttributes'] instanceof Array) {
			for (var n = 0; n < revised['metadata']['rightsAttributes'].length; n++) {
				if (revised['metadata']['rightsAttributes'][n] == 'pd' || revised['metadata']['rightsAttributes'][n] == 'ic' || revised['metadata']['rightsAttributes'][n] == 'und') {
					solr_json['rightsAttributes'] = revised['metadata']['rightsAttributes'][n];
				}
			}
		}
		else {
			solr_json['rightsAttributes'] = revised['metadata']['rightsAttributes'];
		}
	}

	if ('pubDate' in revised['metadata']) {
		solr_json['datePublished'] = revised['metadata']['pubDate'].toString() + '-12-31';
	}

	if ('pubDate' in revised['metadata']) {
		solr_json['yearPublished'] = revised['metadata']['pubDate'].toString();
	}

	if ('publisher' in revised['metadata']) {
		if (revised['metadata']['publisher'] instanceof Array) {
			var publisher = [];
			for (var n = 0; n < revised['metadata']['publisher'].length; n++) {
				if (revised['metadata']['publisher'][n]['name'] instanceof Object) {
					publisher.push(revised['metadata']['publisher'][n]['name']['@value']);
				}
				else {
					publisher.push(revised['metadata']['publisher'][n]['name']);
				}
			}
			solr_json['publisher'] = publisher;
		}
		else {
			solr_json['publisher'] = revised['metadata']['publisher']['name'];
		}
	}

	if ('language' in revised['metadata']) {
		if (revised['metadata']['language'] instanceof Array) {
			var language = [];
			for (var n = 0; n < revised['metadata']['language'].length; n++) {
				language.push(revised['metadata']['language'][n]);
			}
			solr_json['inLanguage'] = language;
		}
		else {
			solr_json['inLanguage'] = revised['metadata']['language'];
		}
	}

	if ('sourceInstitution' in revised['metadata']) {
		solr_json['sourceOrganization'] = revised['metadata']['sourceInstitution']['name'];
	}

	fs.writeFile('./rerun_solr_results/' + handle + '_solr.json', JSON.stringify(solr_json,null,4), function(err) {
		if(err) {
			console.log(err)
			console.log("Couldn't write solr json")
		}
		else {
			console.log("Solr json was saved");
		}
	});
}

fs.readdirSync('./results','utf8').forEach(file => {
//	console.log(file.substring(0,file.indexOf('.json')));
	if (file.indexOf('.json') > -1) {
		buildSolrJSON(file.substring(0,file.indexOf('.json')),JSON.parse(fs.readFileSync('./results/' + file,'utf8')))
	}
})