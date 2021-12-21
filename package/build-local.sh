pip uninstall -y LinkedDicom
rm -R dist/
rm -R LinkedDicom.egg-info/
rm -R build/

python setup.py install
