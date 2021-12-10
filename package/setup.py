from setuptools import setup

setup(
    name='LinkedDicom',
    version='0.1.0',
    author='Johan van Soest',
    author_email='j.vansoest@maastrichtuniversity.nl',
    packages=['LinkedDicom'],
    # scripts=['bin/script1','bin/script2'],
    url='http://pypi.python.org/pypi/LinkedDicom/',
    license='../LICENSE',
    description='A package to extract DICOM header data and store this in RDF',
    long_description=open('../README.md').read(),
    install_requires=[
        "pydicom",
        "rdflib",
        "requests"
    ],
)