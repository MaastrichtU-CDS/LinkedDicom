from LinkedDicom import RDFService
from abc import ABC, abstractmethod
from dicompylercore import dicomparser, dvh, dvhcalc # TODO do not load this module if dicompyler is not used
import rdflib
import json

class DVH_factory(ABC):
    def __init__(self, filePath):
        self.__ldcm_graph = RDFService.GraphService(filePath)
        self.__calculation_graph = RDFService.GraphService()
    
    def get_ldcm_graph(self):
        return self.__ldcm_graph
    
    def get_calculation_graph(self):
        return self.__calculation_graph

    @abstractmethod
    def calculate_dvh(self):
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

    def calculate_dvh(self):
        dcmDosePackages = self.__find_complete_packages()
        for dosePackage in dcmDosePackages:
            print(f"{dosePackage.rtDose} | {dosePackage.rtDosePath} | {dosePackage.rtStructPath} ")
            print(json.dumps(self.__get_dvh_for_structures(dosePackage.rtStructPath, dosePackage.rtDosePath), indent=2))

    
    def __get_dvh_for_structures(self, rtStructPath, rtDosePath):
        if type(rtStructPath) == rdflib.term.URIRef:
            rtStructPath = str(rtStructPath).replace("file://", "")
        structObj = dicomparser.DicomParser(rtStructPath)
        
        if type(rtDosePath) == rdflib.term.URIRef:
            rtDosePath = str(rtDosePath).replace("file://", "")
        doseObj = dicomparser.DicomParser(rtDosePath)

        structures = structObj.GetStructures()
        dvh_list = [ ]
        for index in structures:
            structure = structures[index]
            calcdvh = dvhcalc.get_dvh(rtStructPath, rtDosePath, index)
            structOut = {
                "structureName": structure["name"],
                "min": calcdvh.min,
                "mean": calcdvh.mean,
                "max": calcdvh.max,
                "volume": int(calcdvh.volume),
                "color": structure["color"].tolist(),
                "dvh_d": calcdvh.bincenters.tolist(),
                "dvh_v": calcdvh.counts.tolist()
            }
            dvh_list.append(structOut)
        return dvh_list