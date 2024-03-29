import pydicom
import os
import re
import requests
from LinkedDicom.OntologyService import OntologyService
from LinkedDicom.OntologyService import PropertyType
from LinkedDicom.RDFService import GraphService
from pydicom.tag import Tag

class LinkedDicom:
    def __init__(self, ontology_file_path):
        # Determine external ontology file or embedded in package
        if ontology_file_path is None:
            import pkg_resources
            my_data = pkg_resources.resource_string(LinkedDicom.__name__, "LinkedDicom.owl")
            self.ontologyService = OntologyService(my_data, True)
        else:
            self.ontologyService = OntologyService(ontology_file_path)
        self.graphService = GraphService()
        self.ontologyPrefix = "https://johanvansoest.nl/ontologies/LinkedDicom/"

    def processFolder(self, folderLocation, persistentStorage=False):
        for root, subdirs, files in os.walk(folderLocation):
            for filename in files:
                file_path = os.path.join(root, filename)
                if(file_path.endswith(".dcm") or file_path.endswith(".DCM")):
                    self.parseDcmFile(file_path, persistentStorage=persistentStorage)

    def getTagValueForPredicate(self, dcmHeader, predicate):
        tagString = predicate.replace(self.ontologyPrefix + "T", "")
        tag = Tag("0x" + tagString)
        return dcmHeader[tag].value
    

    def tagToString(self, tag):
        predicate = str(tag).replace("(","")
        predicate = predicate.replace(", ", "")
        predicate = predicate.replace(")", "")
        return predicate
    
    def tagToPredicate(self, tag):
        predicate = self.tagToString(tag)
        predicate = predicate.upper()
        return [ self.ontologyPrefix + "T" + predicate, self.ontologyPrefix + "R" + predicate ]

    def createParentInstances(self, dcmHeader, currentInstance, currentClass):
        domainPredicateList = self.ontologyService.getObjectPredicatesForClassRange(currentClass)
        
        for row in domainPredicateList:
            newClass = row["domain"]
            predicate = row["predicate"]

            keyForInstance = self.ontologyService.getKeyForClass(newClass)
            newInstance = self.graphService.createOrGetInstance(newClass, self.getTagValueForPredicate(dcmHeader, keyForInstance), keyForInstance)

            self.graphService.addPredicateObjectToInstance(newInstance, predicate, currentInstance)

            self.createParentInstances(dcmHeader, newInstance, newClass)

    def parseDcmFile(self, filePath, clearStore=False, persistentStorage=False):
        if clearStore:
            self.graphService = GraphService()
        
        dcmHeader = pydicom.dcmread(filePath, force=True)

        sopClassUid = dcmHeader[Tag(0x8,0x16)].value

        iodClass = self.ontologyService.getClassForUID(sopClassUid)
        keyForInstance = self.ontologyService.getKeyForClass(iodClass)
        sopInstanceUID = self.graphService.createOrGetInstance(iodClass, self.getTagValueForPredicate(dcmHeader, keyForInstance), keyForInstance)

        self.createParentInstances(dcmHeader, sopInstanceUID, iodClass)
        
        if persistentStorage:
            self.graphService.addPredicateLiteralToInstance(sopInstanceUID, self.graphService.replaceShortToUri("schema:contentUrl"), os.path.abspath(filePath))
            self.graphService.addPredicateLiteralToInstance(sopInstanceUID, self.graphService.replaceShortToUri("schema:encodingFormat"), "application/dicom")

        for key in dcmHeader.keys():
            element = dcmHeader[key]

            if element.VR == "SQ":
                self.parseSequence(dcmHeader, element, sopInstanceUID)
            else:
                self.parseElement(dcmHeader, element, None)
        
        if clearStore:
            return self.graphService.getTriplesTurtle()
            
    
    def parseElement(self, dcmHeader, element, currentInstance):
        predicates = self.tagToPredicate(element.tag)

        for predicate in predicates:
            if self.ontologyService.predicateExists(predicate):
                if currentInstance is None:
                    myClass = self.ontologyService.relatedToInformationEntity(predicate)
                    keyforClass = self.ontologyService.getKeyForClass(myClass)
                    currentInstance = self.graphService.createOrGetInstance(myClass, self.getTagValueForPredicate(dcmHeader, keyforClass), keyforClass)

                predicateType = self.ontologyService.getPredicatePropertyType(predicate)
                if predicateType==PropertyType.OBJECT:
                    self.graphService.addPredicateObjectToInstance(currentInstance, predicate, self.graphService.valueAsIri(str(element.value)))
                if predicateType==PropertyType.LITERAL:
                    self.graphService.addPredicateLiteralToInstance(currentInstance, predicate, str(element.value))
    
    def parseSequence(self, dcmHeader, sequenceElement, iodInstance):
        predicates = self.tagToPredicate(sequenceElement.tag)

        for predicate in predicates:
            if self.ontologyService.predicateExists(predicate):
                sequenceClass = self.ontologyService.relatedToSequence(predicate)
                currentSequenceInstance = self.graphService.createOrGetInstance(sequenceClass, iodInstance + "_" + self.tagToString(sequenceElement.tag), None)
                self.graphService.addPredicateObjectToInstance(iodInstance, predicate, currentSequenceInstance)

                for i in range(len(sequenceElement.value)):
                    sequenceItemElement = sequenceElement.value[i]
                    sequenceItemClass = self.ontologyService.getRelatedSequenceItemClass(sequenceClass)
                    currentSequenceItemInstance = self.graphService.createOrGetInstance(sequenceItemClass, currentSequenceInstance + "_" + str(i), None)
                    self.graphService.addPredicateObjectToInstance(currentSequenceInstance, self.ontologyPrefix + "has_sequence_item", currentSequenceItemInstance)

                    for key in sequenceItemElement.keys():
                        element = sequenceItemElement[key]

                        if element.VR == "SQ":
                            self.parseSequence(dcmHeader, element, currentSequenceItemInstance)
                        else:
                            self.parseElement(dcmHeader, element, currentSequenceItemInstance)

    def saveResults(self, location):
        self.graphService.saveTriples(location)
    def postSparqlEndpoint(self, serverUrl, repoName, localGraphName):
        turtle = self.graphService.getTriplesTurtle()

        # upload to RDF store
        loadRequest = requests.post(serverUrl + "/repositories/" + repoName + "/rdf-graphs/" + localGraphName,
            data=turtle, 
            headers={
                "Content-Type": "text/turtle"
            }
        )