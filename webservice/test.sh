docker rmi jvsoest/linkeddicom

cp ../ontology/LinkedDicom.owl ./
docker build --no-cache -t jvsoest/linkeddicom ./
rm ./LinkedDicom.owl

docker run -d --rm \
    -e "SPARQL_ENDPOINT_URL=https://graphdb.jvsoest.eu/repositories/public_dump" \
    -e "ONTOLOGY_LOCATION=/LinkedDicom.owl" \
    -v $(pwd)/../ontology/LinkedDicom.owl:/LinkedDicom.owl \
    -p 80:80 \
    jvsoest/linkeddicom

sleep 10

curl --data-binary "@testfile.dcm" -H "Content-Type: application/dicom" http://localhost/import