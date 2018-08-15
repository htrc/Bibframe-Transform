var fs = require("fs");
var request = require("request");
var jsonld = require('jsonld');

//var handle = 'http://hdl.handle.net/2027/uc1.l0079859914';
function createEF(handle) {
	fs.readFile('./bibframe2ef-V3.rq','utf8', function(err,data) {
		var test_query = data;
		test_query = test_query.replace('?handle_url','<' + handle + '>');

		console.log(test_query);

		request({
			method: 'POST',
			uri: 'https://worksets.htrc.illinois.edu/sparql/',
			headers: {
				'Content-Type': 'application/x-www-form-unencoded',
			},
			form: {
				'default-graph-uri': '',
				'query': test_query,
				'format': 'application/ld+json'
			}
		}, function (er,rs,bd) {
			if (er) {
				res.write("ERROR IN SENDING REQUEST");
				res.write(er);
			}
			else {
				console.log("REQUEST WORKED");
				console.log("Response: %s",bd);

				var promises = jsonld.promises;
				var promise = promises.compact(JSON.parse(bd),'https://worksets.htrc.illinois.edu/context/ef_context.jsonld');
				promise.then(function(compacted) {
					var new_promises = jsonld.promises;
					var new_promise = new_promises.frame(compacted,'https://worksets.htrc.illinois.edu/context/ef_frame.json');
					new_promise.then(function(framed) {
						fs.writeFile('./' + handle.substring(handle.lastIndexOf('/')) + '.json', JSON.stringify(framed,null,4), function(err) {
							if(err) {
								return console.log(err);
							}

							console.log("The file was saved");
						});
					})
				})
			}
		})
	});
}

createEF('http://hdl.handle.net/2027/inu.30000088819010')
/*var handles = ['coo.31924002798605','umn.31951d005322505','uc1.31210002238952','mdp.39015050454712','uc1.b3722085','hvd.32044103043196','mdp.39015049250734','uiug.30112027687059','coo.31924070974831','inu.30000088819010']
for (var i = 0; i < handles.length; i++) {
	createEF('http://hdl.handle.net/2027/' + handles[i]);
}*/