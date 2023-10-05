from LinkedDicom import RDFService
import datetime
from abc import ABC, abstractmethod
from dicompylercore import dicomparser, dvh, dvhcalc # TODO do not load this module if dicompyler is not used
import dicompylercore
from uuid import uuid4
import rdflib
import json
import os

class DVH_factory(ABC):
    def __init__(self, file_or_graph_service):
        if type(file_or_graph_service)==RDFService.GraphService:
            self.__ldcm_graph = file_or_graph_service
        else:
            self.__ldcm_graph = RDFService.GraphService(file_or_graph_service)
    
    def get_ldcm_graph(self):
        return self.__ldcm_graph

    @abstractmethod
    def calculate_dvh(self, folder_to_store_results):
        pass

class DVH_dicompyler(DVH_factory):
    
    def __find_complete_packages(self):
        query = """
            PREFIX ldcm: <https://johanvansoest.nl/ontologies/LinkedDicom/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX schema: <https://schema.org/>

            SELECT ?rtDose ?rtDosePath ?rtStruct ?rtStructPath
            WHERE {
                ?rtPlan rdf:type ldcm:Radiotherapy_Plan_Object.
                
                ?dcmSerieRtPlan ldcm:has_image ?rtPlan.
                ?dcmStudy ldcm:has_series ?dcmSerieRtPlan.
                
                ?dcmStudy ldcm:has_series ?dcmSerieRtStruct.
                ?dcmSerieRtStruct ldcm:has_image ?rtStruct.
                ?rtStruct rdf:type ldcm:Radiotherapy_Structure_Object.
                ?rtStruct schema:contentUrl ?rtStructPath.
                
                ?dcmStudy ldcm:has_series ?dcmSerieRtDose.
                ?dcmSerieRtDose ldcm:has_image ?rtDose.
                ?rtDose rdf:type ldcm:Radiotherapy_Dose_Object.
                ?rtDose schema:contentUrl ?rtDosePath.
            }
            """
        dose_objects = self.get_ldcm_graph().runSparqlQuery(query)
        return dose_objects

    def calculate_dvh(self, folder_to_store_results):
        dcmDosePackages = self.__find_complete_packages()
        results = []
        for dosePackage in dcmDosePackages:
            print(f"Processing {dosePackage.rtDose} | {dosePackage.rtDosePath} | {dosePackage.rtStructPath} ")
            calculatedDose = self.__get_dvh_for_structures(dosePackage.rtStructPath, dosePackage.rtDosePath)
            uuid_for_calculation = uuid4()
            resultDict = {
                  "@context": {
                    "CalculationResult": "https://johanvansoest.nl/ontologies/LinkedDicom-dvh/CalculationResult",
                    "references": {
                        "@id": "https://johanvansoest.nl/ontologies/LinkedDicom-dvh/references",
                        "@type": "@id"
                    },
                    "software": {
                        "@id": "https://schema.org/SoftwareApplication",
                        "@type": "@id"
                    },
                    "version": "https://schema.org/version",
                    "dateCreated": "https://schema.org/dateCreated",
                    "containsStructureDose": {
                        "@id": "https://johanvansoest.nl/ontologies/LinkedDicom-dvh/containsStructureDose",
                        "@type": "@id"
                    },
                    "structureName": "https://johanvansoest.nl/ontologies/LinkedDicom-dvh/structureName",
                    "min": {
                        "@id": "https://johanvansoest.nl/ontologies/LinkedDicom-dvh/min",
                        "@type": "@id"
                    },
                    "mean": {
                        "@id": "https://johanvansoest.nl/ontologies/LinkedDicom-dvh/mean",
                        "@type": "@id"
                    },
                    "max": {
                        "@id": "https://johanvansoest.nl/ontologies/LinkedDicom-dvh/max",
                        "@type": "@id"
                    },
                    "volume": {
                        "@id": "https://johanvansoest.nl/ontologies/LinkedDicom-dvh/volume",
                        "@type": "@id"
                    },
                    "dvh_points": {
                        "@id": "https://johanvansoest.nl/ontologies/LinkedDicom-dvh/dvh_point",
                        "@type": "@id"
                    },
                    "dvh_curve": {
                        "@id": "https://johanvansoest.nl/ontologies/LinkedDicom-dvh/dvh_curve",
                        "@type": "@id"
                    },
                    "d_point": "https://johanvansoest.nl/ontologies/LinkedDicom-dvh/dvh_d_point",
                    "v_point": "https://johanvansoest.nl/ontologies/LinkedDicom-dvh/dvh_v_point",
                    "Gray": "http://purl.obolibrary.org/obo/UO_0000134",
                    "cc": "http://purl.obolibrary.org/obo/UO_0000097",
                    "unit": "@type",
                    "value": "https://schema.org/value",
                    "has_color": "https://johanvansoest.nl/ontologies/LinkedDicom-dvh/has_color"
                },
                "@type": "CalculationResult",
                "@id": "http://data.local/ldcm-rt/" + str(uuid_for_calculation),
                "references": [ dosePackage.rtDose, dosePackage.rtStruct ],
                "software": {
                    "@id": "https://github.com/dicompyler/dicompyler-core",
                    "version": dicompylercore.__version__
                },
                "dateCreated": datetime.datetime.now().isoformat(),
                "containsStructureDose": calculatedDose
            }
            
            if folder_to_store_results is not None:
                filename = os.path.join(folder_to_store_results, f"{uuid_for_calculation}.jsonld")
                with open(filename, "w") as f:
                    json.dump(resultDict, f)
            else:
                results.append(resultDict)
        
        if folder_to_store_results is None:
            return results

    def calculate_dvh_output_triples(self):
        resultTriples = ""
        result_list = self.calculate_dvh(None)
        for ld_dict in result_list:
            # print(ld_dict)
            g = rdflib.Graph()
            g.parse(data=json.dumps(ld_dict), format="json-ld")
            resultTriples += g.serialize(format="nt")
        return resultTriples
    
    def __get_dvh_for_structures(self, rtStructPath, rtDosePath):
        """
        Calculate DVH parameters for all structures available in the RTSTRUCT file.
        Input:
            - rtStructPath: an URIRef or string containing the file path of the RTSTRUCT file
            - rtDosePath: an URIRef or string containing the file path of the RTDOSE file
        Output:
            - A python list containing a dictionaries with the following items:
                - structureName: name of the structure as given in the RTSTRUCT file
                - min: minimum dose to the structure
                - mean: mean dose for this structure
                - max: maximum dose for this structure
                - volume: volume of the structure
                - color: color (Red Green Blue) for the structure on a scale of 0-255
                - dvh_d: list of dose values on the DVH curve
                - dvh_v: list of volume values on the DVH curve
        """

        if type(rtStructPath) == rdflib.term.URIRef:
            rtStructPath = str(rtStructPath).replace("file://", "")
        structObj = dicomparser.DicomParser(rtStructPath)
        
        if type(rtDosePath) == rdflib.term.URIRef:
            rtDosePath = str(rtDosePath).replace("file://", "")
        # doseObj = dicomparser.DicomParser(rtDosePath)

        structures = structObj.GetStructures()
        dvh_list = [ ]
        for index in structures:
            structure = structures[index]
            calcdvh = dvhcalc.get_dvh(rtStructPath, rtDosePath, index)

            dvh_d = calcdvh.bincenters.tolist()
            dvh_v = calcdvh.counts.tolist()
            dvh_points = []
            for i in range(0, len(dvh_d)):
                dvh_points.append({
                    "d_point": dvh_d[i],
                    "v_point": dvh_v[i]
                })

            id = "http://data.local/ldcm-rt/" + str(uuid4())
            structOut = {
                "@id": id,
                "structureName": structure["name"],
                "min": { "@id": f"{id}/min", "unit": "Gray", "value": calcdvh.min },
                "mean": { "@id": f"{id}/mean", "unit": "Gray", "value": calcdvh.mean },
                "max": { "@id": f"{id}/max", "unit": "Gray", "value": calcdvh.max },
                "volume": { "@id": f"{id}/volume", "unit": "cc", "value": int(calcdvh.volume) },
                "color": ','.join(str(e) for e in structure["color"].tolist()),
                "dvh_curve": {
                    "@id": f"{id}/dvh_curve",
                    "dvh_points": dvh_points
                }
            }
            dvh_list.append(structOut)
        return dvh_list