from setuptools import setup, find_packages

setup(
    name='LinkedDicom',
    version='0.3.0',
    author='Johan van Soest',
    author_email='j.vansoest@maastrichtuniversity.nl',
    packages=find_packages(),
    url='https://github.com/MaastrichtU-CDS/LinkedDicom',
    license='Apache 2.0',
    description='A package to extract DICOM header data and store this in RDF',
    long_description="A package to extract DICOM header data and store this in RDF",
    install_requires=[
        "pydicom",
        "rdflib",
        "requests",
        "click",
        "pynetdicom",
        "requests",
        "dicompyler-core"
    ],
    entry_points = {
        'console_scripts': [
            'ldcm-parse = LinkedDicom.cli:main_parse',
            'ldcm-calc-dvh = LinkedDicom.cli:calc_dvh',
            'ldcm-scp = LinkedDicom.CLI_SCP:start_scp'
        ]
    },
    package_data = {
        '': ['*.owl'],
    }
)
