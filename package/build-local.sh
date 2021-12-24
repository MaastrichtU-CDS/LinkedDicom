pip uninstall -y LinkedDicom
rm -R dist/
rm -R LinkedDicom.egg-info/
rm -R build/

cp ../ontology/LinkedDicom.owl LinkedDicom/LinkedDicom.owl

python setup.py install
