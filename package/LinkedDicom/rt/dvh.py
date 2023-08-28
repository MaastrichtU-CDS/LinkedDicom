from LinkedDicom import RDFService
from abc import ABC, abstractmethod

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