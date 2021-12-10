from LinkedDicom import LinkedDicom

liDcm = LinkedDicom.LinkedDicom("../ontology/LinkedDicom.owl")
liDcm.parseHeader("testfile.dcm", clearStore=True)

qRes = liDcm.graphService.runSparqlQuery("""
    SELECT *
    WHERE {
        ?patient rdf:type ldcm:Patient.
        ?patient ?p ?o.
    }
""")
for row in qRes:
    print(f"{row.patient} | {row.p} | {row.o}")