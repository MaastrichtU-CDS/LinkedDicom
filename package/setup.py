from setuptools import setup

setup(
    name='LinkedDicom',
    version='0.2.0',
    author='Johan van Soest',
    author_email='j.vansoest@maastrichtuniversity.nl',
    packages=['LinkedDicom'],
    url='https://github.com/MaastrichtU-CDS/LinkedDicom',
    license='Apache 2.0',
    description='A package to extract DICOM header data and store this in RDF',
    long_description="A package to extract DICOM header data and store this in RDF",
    install_requires=[
        "pydicom",
        "rdflib",
        "requests",
        "click"
    ],
    entry_points = {
        'console_scripts': [
            'ldcm-parse = LinkedDicom.cli:main_parse'
        ]
    },
    package_data = {
        '': ['*.owl'],
    }
)
