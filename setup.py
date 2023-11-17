#!/usr/bin/env python

'''
setup.py: Setup script used for the project.
'''

# Imports
from setuptools import setup, find_packages

# Setup
setup(
    name='signature-adoption',
    version='0.1',
    description='Signature Adoption',
    author='Taylor R. Schorlemmer',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)