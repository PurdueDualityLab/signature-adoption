THIS README IS NOT UP TO DATE

# Table of Contents
1. [Table of Contents](#table-of-contents)
2. [Overview](#overview)
3. [Directory Structure](#directory-structure)
4. [Requirements](#requirements)
    1. [PostgreSQL](#postgresql)
    2. [Big Query Authentication](#big-query-authentication)
    3. [HuggingFace Authentication](#huggingface-authentication)
    4. [Python](#python)
5. [Running](#running)
    1.  [Get Packages](#get-packages)
    2.  [Filter Packages](#filter-packages)
    3.  [Check Adoption](#check-adoption)
    4.  [Create Database](#create-database)
    5.  [Analysis](#analysis)

# Overview
Tools for verifying signatures on PyPI, Docker Hub, Maven Central, and Hugging Face.
This repository contains a collection of scripts that can be used in conjunction to verify signatures on each of the afore mentioned registries.
These scripts require some preliminary setup to collect data.
Many of these scripts are also designed to be paralellized due to the large amount of data on any given registry.
The order of operations for these scripts are as follows:
1. Collect a list of all packages from a given registry
2. Apply filters to that list of packages
3. On the remaining packages, check the adoption of signatures
4. Move the adoption data into a unified database.
5. Perform analysis on the database.

# Directory Structure
```bash
.
├── bigquery.json
├── hftoken.txt
├── README.md
├── setup.py
├── data
│   ├── adoption.db
│   ├── docker
│   ├── huggingface
│   ├── maven
│   ├── pypi
│   └── results
├── logs
└── src
    └── signature_adoption
        ├── __init__.py
        ├── adoption
        ├── analysis
        ├── database
        ├── filter
        ├── packages
        └── util
```
# Requirements
## PostgreSQL
The initial dataset generation script [packages.py](src/packages.py) interfaces with a PostgreSQL database with a data dump from [ecosyste.ms](https://packages.ecosyste.ms/open-data).
Before running the [packages.py](src/packages.py) script, a valid PostgreSQL server should be running with the _packages_production_ database available.
Please be aware that **this database is about 200G when rebuilt**.
By default, the [packages.py](src/packages.py) script is configured to interface with a PostgreSQL server running on the localhost, to change this configuration, you will have to modify the `db_credentials` variable in the code.
The script also checks the `PSQL_Password` environmental variable for a password.
That can be set in linux using the following command:
```bash
export PSQL_Password=<my_psql_password>
```

## Big Query Authentication
[packages.py](src/packages.py) also uses access to Google's BigQuery to fetch data for PyPI.
For this to work, a valid service account key must be added to the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.
This can be accomplished in linux using the following command:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=<creds_file>
```
Check documentation at https://cloud.google.com/docs/authentication/provide-credentials-adc for more information.

## HuggingFace Authentication
[packages.py](src/packages.py) requires an access token to interface with the HuggingFace API.
See your [Hugging Face](https://huggingface.co/settings/tokens) account settings for more details.
Pass a file containing this token to the script in command line.

[adoption.py](src/adoption.py) requires an ssh key to perform git clones of repositories.
Ensure that this machine has a ssh key that is linked to a valid HuggingFace account.
See your [Hugging Face](https://huggingface.co/settings/keys) account settings for more details.

## Python
The scripts for this project are written in Python.
The [setup.py](setup.py) turns this project into an installable Python package.
Using the following command from the base project directory, you can add this package to a Python environment.
```bash
python -m pip install .
```

After installing this package, it can be interfaced with other Python scripts, or referenced directly from the command line using:
```bash
python -m signature-adoption.<module>
```

# Running

## Get Packages
Before checking for signature adoption in each registry, we need to get a list of all packages for each registry. 
For PyPI, NPM, Docker Hub, and Maven Central, we can run the [packages.py](src/packages.py) script to generate a list of packages and versions from each registry.

Hugging Face and PyPI have special arguments. Take a look at these by using `python src/packages.py huggingface -h` and `python src/packages.py huggingface -h` respectively.

## Filter Packages


## Check Adoption


## Create Database


## Analysis


