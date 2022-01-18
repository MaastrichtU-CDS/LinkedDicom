# LinkedDicom

This repository provides a basic version of the LinkedDicom package and project.
You can use this LinkedDicom package as an API to include in your project, or as a command-line utility.
Mind this repository is work-in-progress and has not been finalised yet.

The following content is available:
* The ontology used is available in the folder [./ontology](./ontology).
* The main contents of the python package are available in [./package](./package)
* An example for using the package as a python API is available in [./examples](./examples)
* The docker implementation as webservice is available in [./webservice](./webservice)
* The use as command-line utility is below

## Use as command-line utility
At the moment, there is one command line to parse a given folder. This is done using the `ldcm-parse` command.
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