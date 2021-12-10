from flask import Flask, Response, request, send_file, abort, render_template
import json
from collections import deque
import subprocess
import requests
from LinkedDicom import LinkedDicom
import os

# Read environment variables
sparqlEndpointUrl = "http://localhost:7200/repositories/data"
if "SPARQL_ENDPOINT_URL" in os.environ:
    sparqlEndpointUrl = os.environ["SPARQL_ENDPOINT_URL"]

graphName = "http://linkeddicom.local/"
if "GRAPH_NAME" in os.environ:
    graphName = os.environ["GRAPH_NAME"]

ontologyLocation = "LinkedDicom.owl"
if "ONTOLOGY_LOCATION" in os.environ:
    ontologyLocation = os.environ["ONTOLOGY_LOCATION"]

app = Flask('LinkedDicom Service')

@app.route("/", methods=["GET"])
def index():
    return "What do you want to import?"

@app.route("/import", methods=["POST"])
def importDataDefault():
    return importData()

def importData():
    contentType = request.content_type
    
    triples = None
    if contentType == "application/dicom":
        triples = processDicom(request.data)
    if contentType == "application/x-mirc":
        triples = processDicom(request.data)
    
    postTriples(triples, sparqlEndpointUrl, graphName)

    return "OK"

def processDicom(dcmData):
    fileName = "file.dcm"
    with open(fileName, "wb") as f:
        f.write(dcmData)
    
    liDcm = LinkedDicom.LinkedDicom(ontologyLocation)
    return liDcm.parseDcmFile(fileName, clearStore=True)

def postTriples(triplesTurtle, outputEndpoint, graphName):
    loadRequest = requests.post((outputEndpoint + "/statements?context=%3C" + graphName + "%3E"),
        data=triplesTurtle, 
        headers={
            "Content-Type": "application/x-turtle"
        }
    )
    return loadRequest

app.run(debug=True, host='0.0.0.0', port=80)