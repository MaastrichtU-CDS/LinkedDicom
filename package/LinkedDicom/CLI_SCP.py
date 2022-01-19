from LinkedDicom import LinkedDicom
import click
import os
import uuid
import json
import time
import shutil
from multiprocessing import Process

from pynetdicom import (
    AE, evt,
    StoragePresentationContexts
)

class SCP_handlers:
    def __init__(self):
        # Create association list
        self.__assocFolderDict = { }
        # Create folder where results are actually stored
        self.__dataDir = os.path.join("ldcm_scp_data")
        os.makedirs(self.__dataDir, exist_ok=True)
    
    def handle_assoc_open(self, event):
        """
        Handle the DICOM association open event
        """
        assocId = str(uuid.uuid4())
        self.__assocFolderDict[event.assoc] = {
            "uuid": assocId,
            "directory": os.path.join(self.__dataDir, assocId),
            "dicom_in": {
                "directory": os.path.join(self.__dataDir, assocId, "original"),
                "files": [ ]
            }
        }
        print("association opened " + self.__assocFolderDict[event.assoc]["uuid"])
        os.makedirs(self.__assocFolderDict[event.assoc]["dicom_in"]["directory"])
    def handle_store(self, event):
        """Handle a C-STORE request event."""
        # Decode the C-STORE request's *Data Set* parameter to a pydicom Dataset
        ds = event.dataset

        # Add the File Meta Information
        ds.file_meta = event.file_meta

        # Save the dataset using the SOP Instance UID as the filename
        filePath = os.path.join(self.__assocFolderDict[event.assoc]["dicom_in"]["directory"], ds.SOPInstanceUID + ".dcm")
        ds.save_as(filePath, write_like_original=False)
        self.__assocFolderDict[event.assoc]["dicom_in"]["files"].append(filePath)

        # Return a 'Success' status
        return 0x0000
    def handle_assoc_close(self, event):
        """
        Handle association close, and trigger the analysis
        """
        print("association closed: " + str(self.__assocFolderDict[event.assoc]["uuid"]))
        with open(os.path.join(self.__assocFolderDict[event.assoc]["directory"], "output.json"), "w") as f:
            json.dump(self.__assocFolderDict[event.assoc], f)

        os.system("chmod -R 777 %s" % self.__assocFolderDict[event.assoc]["directory"])
        
        print("Try to start process")
        p = Process(target=run_ldcm, args=(self.__assocFolderDict[event.assoc],))
        p.start()

ontology_file_path = None

@click.command()
@click.argument('port', type=click.INT)
@click.option('-o', '--ontology-file', help='Location of ontology file to use for override.')
def start_scp(port, ontology_file):
    """
    Create a DICOM SCP which can accept C-STORE commands. For every association, an analysis is triggered on association close.
    For every association close, the analysis is triggered in a separate thread.
    """
    ontology_file_path = ontology_file
    scpHandlers = SCP_handlers()
    handlers = [(evt.EVT_C_STORE, scpHandlers.handle_store), (evt.EVT_CONN_OPEN, scpHandlers.handle_assoc_open), (evt.EVT_CONN_CLOSE, scpHandlers.handle_assoc_close)]

    # Initialise the Application Entity
    ae = AE()

    # Add the supported presentation contexts
    ae.supported_contexts = StoragePresentationContexts

    print(f"Starting DICOM SCP on port {port}")

    # Start listening for incoming association requests
    ae.start_server(('', port), evt_handlers=handlers)

def run_ldcm(dict_info):
    # Determine external ontology file or embedded in package
    if ontology_file_path is None:
        import pkg_resources
        my_data = pkg_resources.resource_string(LinkedDicom.__name__, "LinkedDicom.owl")
        ldcm = LinkedDicom.LinkedDicom(my_data, True)
    else:
        ldcm = LinkedDicom.LinkedDicom(ontology_file_path)
    
    dicom_input_folder = dict_info['directory']
    print(f"Start processing folder {dicom_input_folder}. Depending on the folder size this might take a while.")
    
    ldcm.processFolder(dicom_input_folder)

    output_location = os.path.join(dicom_input_folder, "..", f"{dict_info['uuid']}.ttl") 
    ldcm.saveResults(output_location)


    shutil.rmtree(dicom_input_folder)
    print("Stored results in " + output_location)

if __name__=="__main__":
    start_scp()
