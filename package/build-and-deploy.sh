cp ../ontology/LinkedDicom.owl LinkedDicom/LinkedDicom.owl
python -m build
twine upload dist/*