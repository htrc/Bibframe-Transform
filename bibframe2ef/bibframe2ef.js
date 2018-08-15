var fs = require("fs");
var request = require("request");
var jsonld = require('jsonld');

var example_handle = 'http://hdl.handle.net/2027/uc1.l0079859914';
fs.readFile('./bibframe2ef-V3.rq','utf8', function(err,data) {
	var test_query = data;
	test_query = test_query.replace('?handle_url','<' + example_handle + '>');

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
					fs.writeFile('./' + example_handle.substring(example_handle.lastIndexOf('/')) + '.json', JSON.stringify(framed,null,4), function(err) {
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