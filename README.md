# Table of Contents
1. [Table of Contents](#table-of-contents)
2. [Overview](#overview)
3. [Requirements](#requirements)
    1. [PostgreSQL](#postgresql)
    2. [Big Query Authentication](#big-query-authentication)
    3. [Install](#install)
4. [Running](#running)
    1.  [Get Packages](#get-packages)
    2.  [Filter Packages](#filter-packages)
    3.  [Check Adoption](#check-adoption)
    4.  [Analysis](#analysis)
5. [Database Schema](#database-schema)
5. [Citation](#citation)
6. [Data Availability](#data-availability)

# Overview
Tools for verifying signatures on PyPI, Docker Hub, Maven Central, and Hugging Face.
This repository contains a package (sigadopt) that can be used to verify the adoption of signatures on packages from various registries.
This package requires some preliminary setup to collect data.
Many of the functions in this package are designed to be run in parallel.
Sigadopt provides the following data collection and analysis pipeline stages:
1. Collect a list of all packages from a given registry (packages)
2. Apply filters to that list of packages (filter)
3. On the remaining packages, check the adoption of signatures (adoption)
4. Perform analysis on the data. (analysis)

# Requirements
## PostgreSQL
In the packages stage of the pipeline, the Maven Central and Docker Hub package list is generated from a PostgreSQL database with a data dump from [ecosyste.ms](https://packages.ecosyste.ms/open-data).
Before running the **packages** stage of the pipeline, a valid PostgreSQL server should be running with the _packages_production_ database available.
Please be aware that **this database is about 200G when rebuilt**.
By default, sigadopt is configured to interface with a PostgreSQL server running on the localhost.
To change this configuration, you will have to modify the `db_credentials` variable in the source ([maven](src/sigadopt/packages/maven.py) and [pypi](src/sigadopt/packages/pypi.py)).
Sigadopt also checks the `PSQL_Password` environmental variable for a password.
That can be set in bash using the following command:
```bash
export PSQL_Password=<my_psql_password>
```

## Big Query Authentication
Sigadopt also uses Google's BigQuery to fetch data for PyPI in the packages stage of the pipeline.
For this to work, a valid service account key must be added to the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.
This can be accomplished in bash using the following command:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=<creds_file>
```
Check documentation at https://cloud.google.com/docs/authentication/provide-credentials-adc for more information.
Alternatively, you can pass the path to the service account key file as an argument to the sigadopt packages stage.

<!-- ## HuggingFace Authentication -->
<!-- [packages.py](src/packages.py) requires an access token to interface with the HuggingFace API. -->
<!-- See your [Hugging Face](https://huggingface.co/settings/tokens) account settings for more details. -->
<!-- Pass a file containing this token to the script in command line. -->
<!---->
<!-- [adoption.py](src/adoption.py) requires an ssh key to perform git clones of repositories. -->
<!-- Ensure that this machine has a ssh key that is linked to a valid HuggingFace account. -->
<!-- See your [Hugging Face](https://huggingface.co/settings/keys) account settings for more details. -->

## Install
The scripts for this project are written in Python.
The [setup.py](setup.py) turns this project into an installable Python package.
We recommend using a virtual environment to avoid conflicts with other packages.
Using the following command from the base project directory, you can add this package to a Python environment.
```bash
python -m pip install .
```
Note that the above installation will provide an error message if the wheel package is not installed to the Python environment before installing the signature adoption package.

After installing this package, a console script is available to run the various stages of the pipeline.
You can interact with this package using the following command:
```bash
sigadopt -h
```

You can get help with each stage of the pipeline by running:
```bash
sigadopt <stage> -h
```

# Running

## Get Packages
Before checking for signature adoption in each registry, we need to get a list of all packages for each registry. 
This involves running the sigadopt packages command on each registry.
We specify the output database to store the list of packages - this is an SQLite3 database.
Note that Hugging Face requires two commands.
The first command gets the list of packages, and the second command gets the list of commits.
The second command takes much longer to run (about 1 day) and is necessary for the filter stage.
Run the following commands to get the list of packages for each registry:
```bash
sigadopt packages <output_database> maven
sigadopt packages <output_database> pypi -a <path_to_service_account_key>
sigadopt packages <output_database> docker
sigadopt packages <output_database> huggingface
sigadopt packages <output_database> hfcommits
```
Hugging Face and PyPI have special arguments.
Take a look at these by using `sigadopt packages <output_database> huggingface -h` and `sigadopt packages <output_database> pypi -h` respectively.

## Filter Packages
You can apply filters to the database of packages produced in the previous stage.
This is done by running the sigadopt filter command.
You can specify the input and output databases;
the minimum and maximum number of versions; and
the minimum and maximum date.
Note that this stage allows for filtering all packages in one command.
For example, the following command filters all packages with more than 5 versions between 2015 and 2023:
```bash
sigadopt filter -d 2015-01-01 -D 2023-12-31 -v 5 <input_database> <output_database> all
```

## Check Adoption
After filtering the packages, we can check the adoption of signatures on each package.
This is done by running the sigadopt adoption command.
```bash
sigadopt adoption <database> <registry>
```
Note that for this stage, the start and stop commands can be used to specify the range of versions to check.


## Analysis
There are several forms of analysis implemented in this package.
The analysis stage can be run using the following command:
```bash
sigadopt analysis <database> <analysis_type>
```
Note that the table commands are intended to generate LaTeX commands for integration into a paper.
Using the JSON option will generate a JSON file with more readable output.


# Database Schema
This tool creates a database with a series of relational tables.
These tables include `registries`, `packages`, `versions`, `artifacts`, `sig_status`, `signatures`, `sig_check`, `list_packets`, and `pgp_keys`.
This section describes the contents of each table. 
For more information on how the database is structured, see the [database](src/sigadopt/utils/database.py) utility file.

## Registries
This table contains the registries that are being analyzed.
The table has the following columns:
- `id`: The primary key for the table.
- `name`: The name of the registry.

## Packages
This table contains the packages that are being analyzed.
The table has the following columns:
- `id`: The primary key for the table.
- `name`: The name of the package.
- `registry_id`: The foreign key to the registry table.
- `versions_count`: The number of versions for the package.
- `latest_release_date`: The date of the latest release.
- `first_release_date`: The date of the first release.
- `downloads`: The number of downloads for the package.
- `downloads_period`: The period of downloads for the package.

## Versions
This table contains the versions of the packages that are being analyzed.
The table has the following columns:
- `id`: The primary key for the table.
- `package_id`: The foreign key to the package table.
- `name`: The name of the version.
- `date`: The date of the version.

## Artifacts
This table contains the artifacts of the packages that are being analyzed.
The table has the following columns:
- `id`: The primary key for the table.
- `version_id`: The foreign key to the version table.
- `name`: The name of the artifact.
- `type`: The type of the artifact.
- `has_sig`: A boolean indicating if the artifact has a signature.
- `digest`: The digest of the artifact.
- `date`: The date the artifact was created.
- `extensions`: The associated file extensions.

## Sig_Status
This table contains the status of the signatures for the packages that are being analyzed.
The table has the following columns:
- `id`: The primary key for the table.
- `name`: The name of the signature status.

These statuses include: 
- `GOOD`: The signature is valid.
- `NO_SIG`: The artifact has no signature.
- `BAD_SIG`: The signature is invalid.
- `EXP_SIG`: The signature is expired.
- `EXP_PUB`: The public key is expired.
- `NO_PUB`: The public key is missing.
- `REV_PUB`: The public key is revoked.
- `BAD_PUB`: The public key is invalid.
- `OTHER`: Other issues with the signature.

## Signatures
This table contains the signatures for the packages that are being analyzed.
The table has the following columns:
- `id`: The primary key for the table.
- `artifact_id`: The foreign key to the artifact table.
- `type`: The type of the signature.
- `raw`: The raw signature.

## Sig_Check
This table contains the results of the signature checks for the packages that are being analyzed.
The table has the following columns:
- `id`: The primary key for the table.
- `artifact_id`: The foreign key to the artifact table.
- `status`: The foreign key to the sig_status table.
- `raw`: The raw signature check output.

## List_Packets
This table contains information about PGP signatures.
The table has the following columns:
- `id`: The primary key for the table.
- `signature_id`: The foreign key to the signatures table.
- `algo`: The algorithm used for the signature.
- `digest_algo`: The algorithm used for the digest.
- `data`: The number of bits in the signature (key length).
- `key_id`: The key id of the signature.
- `created`: The date the signature was created.
- `expires`: The date the signature expires.
- `raw`: The raw output of the `gpg --list-packets` command.

## PGP_Keys
This table contains information about PGP keys.
The table has the following columns:
- `id`: The primary key for the table.
- `key_id`: The key id of the key.
- `keyserver`: The keyserver the key was found on.
- `raw`: The raw output of the `gpg --list-keys` and `gpg --recv-keys` commands.


# Citation
This repository was used to collect signature adoption data for a paper published in IEEE S&P.
Please cite as:

> T. R. Schorlemmer, K. G. Kalu, L. Chigges, *et al.*, “Signing in four public software package registries: Quantity, quality, and influencing factors,” in *2024 IEEE Symposium on Security and Privacy (SP)*, Los Alamitos, CA, USA: IEEE Computer Society, May 2024.


Or use the following bibtex entry:
```bibtex
@inproceedings{ieee_sp_2024_signing,
    author = {T. R. Schorlemmer and K. G. Kalu and L. Chigges and K. Ko and E.
              Ishgair and S. Bagchi and S. Torres-Arias and J. C. Davis},
    booktitle = {2024 IEEE Symposium on Security and Privacy (SP)},
    title = {Signing in Four Public Software Package Registries: Quantity,
             Quality, and Influencing Factors},
    year = {2024},
    publisher = {IEEE Computer Society},
    address = {Los Alamitos, CA, USA},
    month = {may},
}
```

# Data Availability
The final database used for our paper is available at https://zenodo.org/records/10988566.
This database was created by collecting packages, filtering, and checking adoption.
We used this database to run the analysis portion of our pipeline.
