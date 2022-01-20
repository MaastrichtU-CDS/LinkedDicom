# LinkedDicom

This repository provides a basic version of the LinkedDicom package and project.
You can use this LinkedDicom package as an API to include in your project, or as a command-line utility.
Mind this repository is work-in-progress and has not been finalised yet.

The following content is available:
* The ontology used is available in the folder [./ontology](./ontology).
* The main contents of the python package are available in [./package](./package)
* An example for using the package as a python API is available in [./examples](./examples)
* The use as command-line utility is below

## Installation instructions
Currently, the tool has been tested with Python version 3.8.10.
You can find the installation instructions for python [here](https://www.python.org/downloads/).

Afterwards, you can run the following command to install the package from PyPI:
```
pip install LinkedDicom
```

## Use as command-line utility
At the moment, there are two command line utilities:

- Parsing folders locally using `ldcm-parse`
- A DICOM SCP service using `ldcm-scp`

### Parsing folders locally
This tool can be usefull if you have a (limited) folder of DICOM files and want to create a local turtle file.
A full description of the command is given when executing `ldcm-parse --help`.

A copy of this help is presented below:
```
Usage: ldcm-parse [OPTIONS] DICOM_INPUT_FOLDER

  Search the DICOM_INPUT_FOLDER for dicom files, and process these files. The
  resulting turtle file will be stored in linkeddicom.ttl within this folder

Options:
  -o, --ontology-file TEXT  Location of ontology file to use for override.
  --help                    Show this message and exit.
```

The output is saved in linkeddicom.ttl in the DICOM_INPUT_FOLDER. This data can be used by importing it into an RDF endpoint (such as Apache Jena or GraphDB).

### DICOM SCP service
This tool can be used if you want to start a DICOM SCP service which supports C-STORE commands.
A full description of the command is given when executing `ldcm-scp --help`.

A copy of this help is presented below:
```
Usage: ldcm-scp [OPTIONS] PORT

  Create a DICOM SCP which can accept C-STORE commands. For every association,
  an analysis is triggered on association close. For every association close,
  the analysis is triggered in a separate thread.

Options:
  -o, --ontology-file TEXT    Location of ontology file to use for override.
  -s, --sparql-endpoint TEXT  SPARQL endpoint URL to post the resulting
                              triples towards
  --help                      Show this message and exit.
```

By default, the UUID for the DICOM association is used as filename for the created local turtle file.
If someone uses the optional -s tag, users can send data to a specific SPARQL endpoint (e.g. GraphDB or other SPARQL endpoints). An example URL is given below. Mind that there is a named graph (http://ldcm.local/) specified. This is optional and depends on the REST-API possibilities.

```
ldcm-scp -s "https://graphdb.jvsoest.eu/repositories/public_dump/statements?context\=%3Chttp://ldcm.local/%3E" 104
```

Afterwards, you can send data using DICOM protocol to this service using e.g. [DCMTK](https://dicom.offis.de/dcmtk.php.en). For example using the command below:

```
storescu +r +sd localhost 104 ./
```