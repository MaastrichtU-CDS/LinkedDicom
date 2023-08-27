from LinkedDicom import RDFService
from abc import ABC, abstractmethod

class DVH_factory(ABC):
    def __init__(self, filePath):
        self.__ldcm_graph = RDFService.GraphService(filePath)
        self.__calculation_graph = RDFService.GraphService()
    
    @abstractmethod
    def calculate_dvh(self):
        pass

class DVH_dicompyler(DVH_factory):
    
    def __find_complete_packages():
        query = """
            """

    def calculate_dvh(self):
        return super().calculate_dvh()