# Bibframe-Transform
Transform MARC records to BIBFRAME and add links

This pipeline was setup to turn the MARC files we get from Michigan into BIBFRAME data that is loaded into Virtuoso. This was run once in the summer of 2018. Now we want to run it again on the newest full dataset from October, plus the incrementals provided since then. We also want to use this data to generate the metadata for future runs of Extracted Features.

The following is a description of the pipeline used to create the initial run of BIBFRAME data:

## Remove redundant data from MARC JSON files
[removeRedundant.py](./removeRedundant.py) takes as input a folder containing the JSON files, and outputs a new folder that contains copies of the JSON files where reduntant information has been removed.

For each MARC record processed, `removeRedundant.py` checks a mySQL database for the MARC record's OCLC number. If the OCLC number is there, the record is truncated to just the 001, 035 and 974 fields. If the OCLC number is not present, the record is not modified, and the OCLC number is stored in the database.

### Usage
```python removeRedundant.py [folder name]```
To start the process over from scratch and wipe the database that has already been built up run:
```python removeRedundant.py [folder name] -restart```

### Example files
An example raw JSON file that needs to be processed to remove redundant data can be found in [./examples/marc_json/google_segment_aa](./examples/marc_json/google_segment_aa).

The same file after the redundant data has been removed can be found in [./examples/trimmed_marc_json/google_segment_aa](./examples/trimmed_marc_json/google_segment_aa).

## Convert JSON files into MARCXML
We use an XSL stylesheet provided by the Library of Congress to create BIBFRAME records. This stylesheet takes MARCXML files as input, so we need to convert the MARC JSON files into MARCXML first. The folder containing the trimmed JSON files is input into [convertMARC.py](./convertMARC.py), which uses the pymarc library to run the conversion, and the results are written into a new folder.

__A Note About convertMARC.py:__ This file pulls triple duty. It converts JSON to MARCXML, then calls the XSL stylesheet that converts MARCXML to BIBFRAME, then it calls the the script that adds VIAF, LOC & WorldCat URLs to the converted BIBFRAME files. The comments in this file will denote which section does what, but as-is, this file is meant to go from trimmed JSON to finished BIBFRAME output.

### Usage
```python convertMARC.py [folder name]```
If you already have a folder of MARCXML files that you want to convert to BIBFRAME, you can skip the JSON to MARCXML conversion by adding `-xml` to the input like so:
```python convertMARC.py [folder name] -xml```

### Example files
An example MARCXML built from the example trimmed file can be found in [./examples/trimmed_marc_json_XML_records/google_segment_aa.xml](./examples/trimmed_marc_json_XML_records/google_segment_aa.xml)

## Convert MARCXML files into BIBFRAME
Once we have a folder containing MARCXML files, we need to apply the [marc2bibframe2](https://github.com/dkudeki/marc2bibframe2/tree/9fd817d7e525b52a6de7f5b0b0a5fac035968845) stylesheet provided by the Library of Congress. The version we use is a modified version of LOC's tool. It mas been modified to add the `<bf:Item>` structure, which contains the data from MARC's 974 field, and to remove a number of other fields we decided were unneeded for our purposes.

In case you aren't familiar with the BIBFRAME structure, each MARC record is turned into three different nodes: `<bf:Item>`, `<bf:Instance>`, `<bf:Work>`. The Item and Work both have field that point to the Instance, and the Instance has fields that points to the Item and the Work. Within the XML structure, the Item, Instance and Work nodes are all siblings.

### Usage
```python convertMARC.py [folder name]```
If you already have a folder of MARCXML files that you want to convert to BIBFRAME, you can skip the JSON to MARCXML conversion by adding `-xml` to the input like so:
```python convertMARC.py [folder name] -xml```

### Example files
An example BIBFRAME file built from the example trimmed file can be found in [./examples/trimmed_marc_json_BIBF_records/google_segment_aa.xml](./examples/trimmed_marc_json_BIBF_records/BIBF_google_segment_aa.xml)

## Enhance converted BIBFRAME by adding Linked Data URLs
We are able to use services provided by VIAF, WorldCat and LOC to add URLs to enhance the BIBFRAME records we have created. `convertMARC.py` passes each BIBFRAME file to [postConversionTransform.py](./postConversionTransform.py) add the new data to the existing BIBFRAME files.

Here is some info about the three services we call:
#### WorldCat
The vast majority of the records we process have OCLC numbers. When we generate the BIBFRAME, we use a record's OCLC number to generate an id for the `<bf:Instance>` object, but the associated `<bf:Work>` is assigned an arbitrary blank node value. But the URL we use as the Instance id can be used to find what the Work id should be, simply by adding `.jsonld` to the end of it and parsing the results.

Because this data connects relevant nodes to each other, it is important for the structure of the Virtuoso database.

#### VIAF
We can add VIAF URLs to contribution agents that appear in a BIBFRAME record by calling VIAF's AutoSuggest API. The call is `http://www.viaf.org/viaf/AutoSuggest?query=` plus a normalized version of the contribution agent's label string. If there is one result of the correct cotributor type (personal vs corporate), then we use that as the id for the agent. If there are multiple results of the correct type, we avoid the time sink of choosing one or the other by just minting our own unique internal id for the agent. We also mint a unique id when there is no valid result.

This is the only data we add that appears in the metadata we generate from the BIBFRAME files.

__Resources:__ Specifications on the VIAF AutoSuggest API can be found [here](https://www.oclc.org/developer/develop/web-services/viaf/authority-cluster.en.html)

#### LCSH
When a record has a topic agent or a subject agent, we search LOC for that agent. We build our search query to follow the format:
```'https://id.loc.gov/search/?q=' + agent_string + '+rdftype:' + agent_type + '&q=cs%3Ahttp%3A%2F%2Fid.loc.gov%2Fauthorities%2Fsubjects'```
`agent_string` is the subject/topic string
`agent_type` is going to be one of the following values: 'CorporateName', 'FamilyName', 'Topic'. 'Geographic', or 'ComplexSubject'. The values here depend on what the listed `rdf:type` is in the BIBFRAME

This gives us the results for the search term with a specific rdftype to narrow things down. The results are an HTML page. If an exact match for the search term is found in one of the results, the link for that result (which is an LCSH URL) is selected.

__Resources:__ Some basic discussion of searching LOC can be found [here](https://id.loc.gov/techcenter/searching.html).

#### Limits to these services
I haven't been able to find any listed limits to any of these specific services. And nothing in `postConversionTransform.py` specifically sets limits for any of the services. I never was explicitly blocked for a period of time, though the initial run went on long enough that some of thses services had downtime while I was querying them.

If the server is giving bad responses, but I have reason to believe it is just having trouble and will be up soon, I pause for six seconds after every bad response to avoid overloading it, but the siz seconds just a rule of thumb from using other OCLC-related APIs with limits.

### Usage
`postConversionTransform.py` is called by `convertMARC.py`, so typically you'd just want to call `convertMARC.py` as discussed above. `convertMARC.py` calls it by importing `postConversionTransform.py` and calling `postConversionTransform.postConversionTransform(file_name)` where `file_name` is the BIBFRAME file that will be processed.

### Example files
An example of the BIBFRAME file from the last step populated with additional links can be found in [./examples/enhanced_trimmed_marc_json_BIBF_records/BIBF_google_segment_aa.xml](./examples/enhanced_trimmed_marc_json_BIBF_records/BIBF_google_segment_aa.xml)

## Using the BIBFRAME files
The BIBFRAME files from the initial run were saved into Virtuoso and became part of those services. While generating metadata for the TDM project, the Virtuoso was queried for each individual record we were looking for, and the results were framed and modified by a node.js script. This was a slow process and took about a month for 500,000 records.

A faster method would be to use and XSL stylesheet to directly convert the BIBFRAME files into the metadata format we want. Code for both the Virtuoso queries and the XSL stylesheets can be found in [this repo](https://github.com/dkudeki/bibframe2ef).