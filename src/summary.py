#!/usr/bin/env python

'''summary_data.py: This script summarizes the results from all the collection
scripts into a single file.'''


# Import statements
import json
import os
import sys
import csv

# authorship information
author = "Taylor R. Schorlemmer"
email = "tschorle@purdue.edu"


# Load dates
with open('./dates.txt', 'r') as f:
    dates = f.read().splitlines()

# Hugging Face
hf_data = None
hf_file = './HuggingFace/data/verification_data_3_sorted.json'

with open(hf_file, 'r') as f:
    hf_data = json.load(f)

hf_consolodated = {}
for indx in range(len(dates) - 1):
    hf_consolodated[dates[indx]] = {
        "total_packages": hf_data[dates[indx] + " 00:00:00"]["total_packages"],
        "total_commits": hf_data[dates[indx] + " 00:00:00"]["total_commits"],
        "signed_commits": hf_data[dates[indx] + " 00:00:00"]["signed_commits"],
        "unsigned_commits": hf_data[dates[indx] + " 00:00:00"]["unsigned_commits"],
        "valid_signed_commits": hf_data[dates[indx] + " 00:00:00"]["valid_signed_commits"],
        "invalid_signed_commits": hf_data[dates[indx] + " 00:00:00"]["invalid_signed_commits"],
        "signed_packages": hf_data[dates[indx] + " 00:00:00"]["signed_packages"],
        "unsigned_packages": hf_data[dates[indx] + " 00:00:00"]["unsigned_packages"],
    }

del hf_data

# PyPI
py_data = None
py_base_path = './PyPI/data/'
py_consolodated = {}

for indx in range(len(dates) - 1):
    py_file = py_base_path + f'adoption_{dates[indx]}_{dates[indx+1]}.json'
    with open(py_file, 'r') as f:
        py_data = json.load(f)
    py_consolodated[dates[indx]] = {
        "total_packages": py_data["total_packages"],
        "total_signed": py_data["total_signed"],
        "total_unsigned": py_data["total_unsigned"],
        "total_signed_valid": py_data["total_signed_valid"],
        "total_signed_invalid": py_data["total_signed_invalid"],
    }

del py_data

# Write to file

with open('./summary_data.json', 'w') as f:
    json.dump({
        "HuggingFace": hf_consolodated,
        "PyPI": py_consolodated
    }, f, indent=4) 