#!/usr/bin/env python

'''check_adoption.py: This script checks the adoption of signatures for packages from PyPI.
'''

import csv
import json
import sys
import subprocess
import time
import re
import logging as log
from datetime import datetime


# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'



def url_construction(line) -> str:
    

    prefix = "https://files.pythonhosted.org/packages/"
    hash_digest = line['blake2_256_digest']
    hash_section = f"{hash_digest[0:2]}/{hash_digest[2:4]}/{hash_digest[4:]}/"

    url = prefix + hash_section + line['filename']

    return url



if __name__ == "__main__":

    ''' while looking around, have not found many concrete methods to go about validating these signatures.
    one common method brought up in many threads is to use gpg --verify {pkg}.asc {pkg}, but am running into issues
    with obtaining the .asc files when testing manually. looking to see if i can simply run an os.system command in a loop 
    on all pkgs in .csv file. '''

    csv_file = sys.stdin
    infile = csv.DictReader(csv_file)
    log_file = f'/home/tschorle/PyPI/check_log_{sys.argv[1]}.csv'

    print(log_file)

    valid_count = 0
    total_count = 0

    print(time.localtime())

    with open(log_file, 'a', newline='') as logger:

        logger_writer = csv.writer(logger)

        for line in infile:

            filename = line['filename']
            url = url_construction(line)

            ### need to use data in each line of .csv to first do wget on the correct urls, then run the gpg statement
            subprocess.run(['wget', url], capture_output=True)
            subprocess.run(['wget', url+'.asc'], capture_output=True)

            # os.system(f"wget {url}")
            # os.system(f"wget {url}.asc")
            # os.system("clear")

            time.sleep(0.001)
            ### based on return msg of gpg command, can then assess validity of signature
            output = subprocess.run(["gpg", "--keyserver-options", "auto-key-retrieve", 
            "--keyserver", "keyserver.ubuntu.com", "--verify", f"{filename}.asc", f"{filename}"], capture_output=True)

            if re.search("Good signature", str(output.stderr)):
                valid_count += 1

            total_count += 1

            logger_writer.writerow([line['name'], line['version'], line['filename'], line['python_version'], line['blake2_256_digest'], output.stdout, output.stderr])

            subprocess.run(['rm', '-r', filename])
            subprocess.run(['rm', '-r', filename+'.asc'])

        #     ### should probably remove packages at the end of the loop to prevent any buildup
        #     os.system(f"rm -r {filename}")
        #     os.system(f"rm -r {filename}.asc")
    
    print(time.localtime())


    # print(f"Valid signatures: {valid_count}\nTotal signatures: {total_count}")