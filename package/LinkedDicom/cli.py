#!/usr/bin/env python

from LinkedDicom import LinkedDicom
import argparse
import os
import click

@click.command()
@click.argument('dicom-input-folder', type=click.Path(exists=True))
@click.option('-o', '--ontology-file', help='Location of ontology file to use for override.')
def main_parse(dicom_input_folder, ontology_file):
    """
    Search the DICOM_INPUT_FOLDER for dicom files, and process these files.
    The resulting turtle file will be stored in linkeddicom.ttl within this folder
    """
    ldcm = None
    
    ontology_file_path = ontology_file
    if ontology_file_path is None:
        import pkg_resources
        my_data = pkg_resources.resource_string(LinkedDicom.__name__, "LinkedDicom.owl")
        ldcm = LinkedDicom.LinkedDicom(my_data, True)
    else:
        ldcm = LinkedDicom.LinkedDicom(ontology_file_path)

    print(f"Start processing folder {dicom_input_folder}. Depending on the folder size this might take a while.")
    
    ldcm.processFolder(dicom_input_folder)
    
    output_location = os.path.join(dicom_input_folder, "linkeddicom.ttl") 
    ldcm.saveResults(output_location)
    print("Stored results in " + output_location)

if __name__=="__main__":
    main_parse()