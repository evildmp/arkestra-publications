from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='Arkestra publications',
    version='0.0.2',
    author='Ben Rowett and Daniele Procida',
    author_email='daniele@vurt.org',
    packages=find_packages(),
    include_package_data=True,
    zip_safe = False,
    license='LICENCE.txt',
    description='Symplectic Publications integration & output for Arkestra',
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    install_requires=[
        'elementtree',
        'unicodecsv',
    ]
)      
