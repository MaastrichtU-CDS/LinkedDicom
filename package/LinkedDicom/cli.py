#!/usr/bin/env python

from LinkedDicom import LinkedDicom
from LinkedDicom.rt import dvh
import os
import click

@click.command()
@click.argument('dicom-input-folder', type=click.Path(exists=True))
@click.option('-o', '--ontology-file', help='Location of ontology file to use for override.')
@click.option('-fp', '--file-persistent', is_flag=True, default=False, help='Store file path while parsing metadata.')
def main_parse(dicom_input_folder, ontology_file, file_persistent):
    """
    Search the DICOM_INPUT_FOLDER for dicom files, and process these files.
    The resulting turtle file will be stored in linkeddicom.ttl within this folder
    """
    ldcm = LinkedDicom.LinkedDicom(ontology_file)

    print(f"Start processing folder {dicom_input_folder}. Depending on the folder size this might take a while.")
    
    ldcm.processFolder(dicom_input_folder, persistentStorage=file_persistent)
    
    output_location = os.path.join(dicom_input_folder, "linkeddicom.ttl") 
    ldcm.saveResults(output_location)
    print("Stored results in " + output_location)

@click.command()
@click.argument('ldcm-rdf-location', type=click.Path(exists=True))
@click.argument('output_location', type=click.Path(exists=False))
@click.option('-rt', '--reference_type', help="Define the method of reference between RTDose and RTPlan. Default is 'seq_ref'", default="seq_ref")
def calc_dvh(ldcm_rdf_location, output_location, reference_type):
    dvh_factory = dvh.DVH_dicompyler(ldcm_rdf_location)

    ref_type = dvh.RT_Query_Type.RT_DIRECT_REFERENCES
    if reference_type=="seq_ref":
        ref_type = dvh.RT_Query_Type.RT_DIRECT_REFERENCES
    if reference_type=="study":
        ref_type = dvh.RT_Query_Type.DICOM_STUDY

    dvh_factory.calculate_dvh(output_location, reference_type=ref_type)

if __name__=="__main__":
    main_parse()
