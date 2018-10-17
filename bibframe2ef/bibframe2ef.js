var fs = require("fs");
var request = require("request");
var jsonld = require('jsonld');
var Q = require('q');
var async = require('async');

function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve,ms));
}

async function pause() {
	console.log("Giving the server 10 seconds to come back up");
	await sleep(10000);
	console.log("Retrying");
} 

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

	fs.writeFile('./solr_results/' + handle.substring(27).replace(/\//g,'=').replace(/\:/g,'+') + '_solr.json', JSON.stringify(solr_json,null,4), function(err) {
		if(err) {
			console.log("Couldn't write solr json")
		}
		console.log("Solr json was saved");
	});
}

function processResults(bd,handle,doneCallback) {
	try {
		console.log("REQUEST WORKED");
		console.log("Response: %s",bd);
		var json_bd = JSON.parse(bd)
		for (section in json_bd['@graph']) {
			if ('http://schema.org/isAccessibleForFree' in json_bd['@graph'][section]) {
				if (json_bd['@graph'][section]['http://schema.org/isAccessibleForFree'][0]['@value'] == "true") {
					json_bd['@graph'][section]['http://schema.org/isAccessibleForFree'][0]['@value'] = true;
				}
				else {
					json_bd['@graph'][section]['http://schema.org/isAccessibleForFree'][0]['@value'] = false;
				}
			}
		}

		var promises = jsonld.promises;
		var promise = promises.frame(json_bd,'https://worksets.htrc.illinois.edu/context/ef_context.json');
		promise.then(function(framed) {
			console.log(JSON.stringify(framed,null,4));
			var revised = framed;
			delete revised['@context'];
			revised['metadata'] = revised['metadata'][0];

			if (revised['metadata']['sourceInstitution'] instanceof Array) {
				for (var src of revised['metadata']['sourceInstitution']) {
					delete revised['metadata']['sourceInstitution'][src]['id'];
				}
			}
			else {
				delete revised['metadata']['sourceInstitution']['id'];
			}

			if (revised['metadata']['genre'] instanceof Array) {
				let genre_list = []
				for (var i = 0; i < revised['metadata']['genre'].length; i++) {
					if (revised['metadata']['genre'][i].indexOf('_:') == -1) {
						genre_list.push(revised['metadata']['genre'][i]);
					}
				}
				revised['metadata']['genre'] = genre_list;
			}
			else {
				if (revised['metadata']['genre'].indexOf('_:') > -1) {
					delete revised['metadata']['genre'];
				}
			}

			if ('identifier' in revised['metadata']) { 
				if (revised['metadata']['identifier'] instanceof Array) {
					for (var id_index = 0; id_index < revised['metadata']['identifier'].length; id_index++) {
						if (revised['metadata']['identifier'][id_index]['propertyID'] == 'lccn') {
							revised['metadata']['identifier'][id_index]['value'] = revised['metadata']['identifier'][id_index]['value'].replace(/\s/g,'');
						} else {
							delete revised['metadata']['identifier'][id_index]['id'];
						}
					}
				}
				else {
					if (revised['metadata']['identifier']['propertyID'] == 'lccn') {
						revised['metadata']['identifier']['value'] = revised['metadata']['identifier']['value'].replace(/\s/g,'');
					} else {
						delete revised['metadata']['identifier']['id'];
					}
				}
			}

			revised['metadata']['pubDate'] = parseInt(revised['metadata']['pubDate']);

			buildSolrJSON(handle,revised);

			fs.writeFile('./results/' + handle.substring(27).replace(/\//g,'=').replace(/\:/g,'+') + '.json', JSON.stringify(framed,null,4), function(err) {
				if(err) {
					var return_object = {}
					return_object[handle.substring(27)] = "FAILED";
					return doneCallback(err,return_object);
				}

				console.log("The file was saved");
				var return_object = {}
				return_object[handle.substring(27)] = "SUCCESS";
				console.log(return_object);

				return doneCallback(null,return_object);
			});
		});
		promise.catch(function(err) {
			console.log("Reached Catch.");
			pause();
			return processResults(bd,handle,doneCallback);
		});
	} catch (err) {
		var return_object = {}
		return_object[handle.substring(27)] = "FAILED";
		return doneCallback(null,return_object);
	}
}

function sendQuery(filename,handle,doneCallback) {
	progression = { './bibframe2ef.rq': './bibframe2ef_abridged.rq', './bibframe2ef_abridged.rq': './bibframe2ef_very_abridged.rq', './bibframe2ef_very_abridged.rq': './bibframe2ef_extremely_abridged.rq' }
	fs.readFile(filename,'utf8',function(err,data) {
		var query = data;
		query = query.replace('?handle_url','<' + handle + '>');
		console.log(query);

		try {
			request({
				method: 'POST',
				uri: 'https://worksets.htrc.illinois.edu/sparql/',
				headers: {
					'Content-Type': 'application/x-www-form-unencoded',
				},
				form: {
					'default-graph-uri': '',
					'query': query,
					'format': 'application/ld+json'
				}
			}, function (er,rs,bd) {
				if (er) {
					console.log("ERROR IN SENDING REQUEST");
					console.log(er);


					var return_object = {};
					return_object[handle.substring(27)] = "FAILED";
					return doneCallback(null,return_object);
				}
				else {
					if (bd.indexOf('504 Gateway Time-out') == -1) {
						return processResults(bd,handle,doneCallback)
					}
					else {
						if (filename in progression) {
							sendQuery(progression[filename],handle,doneCallback);
						}
						else {
							var return_object = {};
							return_object[handle.substring(27)] = "FAILED";
							return doneCallback(null,return_object);
						}
					}
				}
			})
		}
		catch (err) {
			var return_object = {}
			return_object[handle.substring(27)] = "FAILED";
			return doneCallback(null,return_object);
		}
	});
}

function createEF(handle,doneCallback) {
	handle = 'http://hdl.handle.net/2027/' + handle;
	sendQuery('./bibframe2ef.rq',handle,doneCallback);
}

function onComplete(err,results) {
	console.log("DONE");
	if (err) {
		console.log(err);
	}
	else {
		var text_results = "'volume','status'\n";
		console.log("Final results: ");
		console.log(results);
		for (var index = 0; index < results.length; index++) {
			text_results += Object.keys(results[index]) + "," + results[index][Object.keys(results[index])] + '\n';
		}
		console.timeEnd("batch");
		fs.writeFile('./results.csv',text_results,function(err) {
			if (err) {
				return console.log(err);
			}
			else {
				console.log("Wrote CSV");
			}
		})
	}
}

console.time("batch");
var results = {}
//createEF('http://hdl.handle.net/2027/uc1.l0052148335')
//var working_handles = ['miua.0637578.0075.001','uc1.l0064719099','uc1.b4567945','uc1.l0061128666','coo.31924002798605','umn.31951d005322505','uc1.31210002238952','hvd.32044103043196','mdp.39015049250734','uiug.30112027687059']
//var handles = ["coo.31924002798605","coo.31924062872209","mdp.39015031084372","mdp.39015045822981","mdp.39015064487310","nyp.33433071387322","nyp.33433074827415","nyp.33433075903710","uc1.b3908258","uc2.ark:/13960/t0ns0nn5d","uc2.ark:/13960/t15m64v8t","uc2.ark:/13960/t2x34nv48","uc2.ark:/13960/t4dn40k1s","uc2.ark:/13960/t5k932p0g","bc.ark:/13960/t5q822921","chi.086616114","chi.086751760","chi.086753788","chi.086149971","wu.89094201613","bc.ark:/13960/t3hx2376m","chi.086756689","chi.086752562","chi.086753110","bc.ark:/13960/t8cg0g26t","chi.14407455","chi.14409520","chi.14414574","chi.78884030","chi.78884441","chi.65393760","coo.31924001501307","chi.15464843","chi.16714868","chi.102003209","chi.102003217","chi.102003267","chi.102003275","chi.102003330","chi.102003398","chi.102003453","chi.102003518","chi.102003576","chi.102003631","chi.17016489","chi.20412793","chi.73746353","chi.73746473","chi.57099346","coo.31924001131014","coo.31924001071814","coo.31924001555303","coo.31924001555311","coo.31924001555329","coo.31924001555337","coo.31924001555345","coo.31924001555352","coo.31924001555360","coo.31924001555378","coo.31924001555386","coo.31924001555394","coo.31924001555402","coo.31924001027428","chi.64438248","chi.57054523","chi.57054496","chi.57054530","coo.31924001129141","coo.31924000955025","coo.31924001567324","coo.31924001504806","coo.31924001070188","coo.31924001124746","coo.31924061444141","coo.31924052800061","coo.31924052800087","coo.31924069167488","coo.31924069167462","coo.31924069167470","coo.31924069167496","coo.31924003687658","coo.31924017360631","coo.31924017360656","coo.31924003021510","coo.31924067086888","coo.31924061324913","coo.31924061324921","coo.31924061324939","coo.31924061324947","coo.31924003014358","coo.31924018544092","coo.31924018336499","coo.31924002869216","coo.31924018244719","coo.31924018280713","coo.31924001760515","coo.31924018376446","coo.31924018444186","coo.31924018278493","coo.31924018267108"]
//var handles = ['uc1.l0052148335','uc1.l0079859914'];
//var handles = ['uc2.ark:/13960/t4dn40k1s']
//var handles = ['chi.102003209']

function processHandleList(handles,results) {
	async.mapLimit(handles,5,createEF,onComplete)
}

var read_file = 'biology_workset.csv';
//var read_file = './sample1.csv';

fs.readFile(read_file,'utf8',function(err,data) {
	var lines = data.split('\n');
	var handles = []
	var files = fs.readdirSync('./results');
	for (var i = 1; i < lines.length; i++) {
		var handle = lines[i].substring(1,lines[i].indexOf(',')-1);
		var file_name = handle + '.json';

		if ( handle != '' && files.indexOf(file_name.replace(/\//g,'=').replace(/\:/g,'+')) == -1) {
			console.log(handle.replace(/\//g,'=').replace(/\:/g,'+'));
			handles.push(handle);
		}
	}
	handles = ['mdp.39015013324911']

	processHandleList(handles,results);
})

process.on('uncaughtException', (err) => {
  console.log(`Caught exception: ${err.stack}\n`);
});