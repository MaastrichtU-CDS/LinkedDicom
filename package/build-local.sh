pip uninstall -y LinkedDicom
cp ../ontology/LinkedDicom.owl LinkedDicom/LinkedDicom.owl
python -m build
pip install ./dist/LinkedDicom-0.2.1-py3-none-any.whl