#!/usr/bin/env python

'''
setup.py: Setup script used for the project.
'''

# Imports
from setuptools import setup, find_packages

# Setup
setup(
    name='sigadopt',
    version='0.1',
    description='Signature Adoption',
    author='Taylor R. Schorlemmer',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'matplotlib',
        'huggingface-hub',
        'psycopg2-binary',
        'google-cloud-bigquery',
        'beautifulsoup4',
        'GitPython',
        'json2latex'
    ],
    entry_points={
        'console_scripts': [
            'sigadopt = sigadopt.__main__:main'
        ],
    },
)
