''' setup for pyautoQC '''
import setuptools

setuptools.setup(
    name="pyautoQC",
    version="0.0.1",
    author="Raphael Dussin",
    author_email="raphael.dussin@gmail.com",
    description=("A package to do QC on climate model outputs"),
    license="GPLv3",
    keywords="",
    url="https://github.com/raphaeldussin/pyautoQC",
    packages=['pyautoQC'],
    scripts=['pyautoQC/exe/qc_check_metadata',
             'pyautoQC/exe/qc_check_data']
)
