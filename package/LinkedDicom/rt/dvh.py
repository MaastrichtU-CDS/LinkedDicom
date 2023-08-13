from LinkedDicom import RDFService
from abc import ABC, abstractmethod

class DVH_factory(ABC):
    def __init__(self, filePath):
        self.__graph_service = RDFService.GraphService(filePath)
    
    def __inspect_qualifying_rtdose(self):
        self.__graph_service.runSparqlQuery()