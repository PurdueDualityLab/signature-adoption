from operator import index
import requests as rq
from bs4 import BeautifulSoup
import subprocess as sb
import os
import sys
import concurrent.futures
import csv
import fcntl
import re
import argparse

import threading
from functools import partial
import multiprocessing

import pandas as pd 
import numpy as np


# names = ['package_name', 'version', 'file_name', 'signature_date', 'signature_key', 'request_key', 'signature_validity',
#             'signature_trusted', 'signature_indication', 'primary_key_fingerprint']
# lists = {name: [] for name in names}



# For local tesitng
local = False
# var to specify generated csv files
csv_num = 0
# Lock to preserve variables
lock = threading.Lock()

# lib_name = 'software'


# Get a list of directories from the current directory
def get_dirs(repo_url):
    
    # Extract the versions from the HTML content
    dirs = []
    response = rq.get(repo_url)
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        for a_tag in soup.find_all("a"):
            href = a_tag.get("href")
            if '/' in href:
                dirs.append(href)
        # Don't include the ../ dirs[0] (previous directory)
        return dirs[1:]
    return dirs

# Return a list of signature file pairs ex)[[.asc, .pom], ... ]
def find_pairs(repo_url):

    pairs = []
    response = rq.get(repo_url)
    sign_found = False
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        
        a_tags = soup.find_all("a")[1:]
        if not a_tags:
            # Case 1: It's an empty directory
            append_invalids(repo_url, 'Empty directory')
            return pairs
        for a_tag in a_tags:
            pair = []
            href = a_tag.get("href")
            asc_ind = href.find('.asc')
            if asc_ind != -1:
                sign_found = True
                if asc_ind + 4 == len(href):
                    pair.append(href)
                    temp_pom = href[:len(href)-4]
                    pair.append(temp_pom)
                    pairs.append(pair)
    # Case 2: No signature file found
    if not sign_found:
        append_invalids(repo_url, 'No signature file found')
    return pairs

# write_from: data file & sign file, write_to: root_pkg dir in scratch space
def write_file(write_from, write_to):
    
    # file already exists in scratch space
    if os.path.exists(write_to):
        return True
    file_response = rq.get(f'{write_from}')
    if file_response:
        with open(write_to, "wb") as file:
            file.write(file_response.content)
    # not able to be downloaded
    else:
        with lock:
            # Case 3: invalid urls: data/sign file
            append_invalids(write_from, 'Unable to download, bad url')
            return False
    return True

# generates a list to append to a csv filename
def append_row(filename, row):
    
    with open(filename, 'a') as file:
        fcntl.flock(file, fcntl.LOCK_EX)  # Acquire an exclusive lock

        writer = csv.writer(file)
        writer.writerow(row)

        fcntl.flock(file, fcntl.LOCK_UN)  # Release the lock

# separate csv file for invalid cases
def append_invalids(url, reason):
    
    global local
    
    columns=['url', 'reason']
    
    dirpath = '/scratch/bell/ko112/maven_csvs/invalid_csvs/'
    if local:
        dirpath = 'maven_csvs/invalid_csvs/'
    os.makedirs(dirpath, exist_ok=True)
    csv_path = dirpath + f'maven_invalids.csv'
    if not os.path.exists(csv_path):
        df = pd.DataFrame(columns=columns)
        df.to_csv(csv_path)
    
    new_row = ['', url, reason]

    append_row(csv_path, new_row)

# append one row a at a time to maven_{root_pkg}.csv
def append_signatures(sign_from, signature):
    
    global local
    global lib_name

    columns=['package_name', 'version', 'file_name', 'url', 'raw_output', 'signature_date', 'signature_key', 'request_key',
              'signature_validity', 'signature_trusted', 'signature_indication', 'primary_key_fingerprint']
    # include /com after valid_csvs/ when running individual directory
    dirpath = f'/scratch/bell/ko112/maven_csvs/valid_csvs/'
    if local:
        dirpath = 'maven_csvs/valid_csvs/'
    os.makedirs(dirpath, exist_ok=True)
    # ['https:', '', 'repo1.maven.org', 'maven2', 'engineer', 'echo', 'happymaven', '0.0.1', 'abc.asc']
    splitted = sign_from.split('/')
    # change this to 5 when doing aws/, com/
    root_pkg = splitted[4]
    csv_path = dirpath + f'maven_{root_pkg}.csv'
    if not os.path.exists(csv_path):
        df = pd.DataFrame(columns=columns)
        df.to_csv(csv_path)

    new_row = format_output(str(signature))
    version = splitted[-2]
    filename = splitted[-1]
    package_name = '/' + '/'.join(splitted[4:-2]) + '/'
    url = sign_from
    new_row = ['', package_name, version, filename, url] + new_row

    append_row(csv_path, new_row)


# Downloads sign_file & data_file pairs into the scratch space
def download_files(repo_url):

    global local
    signatures = []

    pairs = find_pairs(repo_url)

    dirpath = '/scratch/bell/ko112/maven_files/'
    if local:
        dirpath = 'maven_files/'
    os.makedirs(dirpath, exist_ok=True)
    for pair in pairs:
        
        sign_from = f'{repo_url}{pair[0]}'
        sign_to = f'{dirpath}{pair[0]}'

        data_from = f'{repo_url}{pair[1]}'
        data_to = f'{dirpath}{pair[1]}'
        
        executor = concurrent.futures.ThreadPoolExecutor()

        arguments = [(sign_from, sign_to), (data_from, data_to)]
        futures = [executor.submit(write_file, arg[0], arg[1]) for arg in arguments]
        results = [future.result() for future in futures]
        # if both files are valid and are stored in scratch space, verify the results
        if bool(results[0]) and bool(results[1]):
            
            signature = verify_signature(sign_to, data_to)
            os.remove(sign_to)
            os.remove(data_to)
            
            append_signatures(sign_from, signature)
            # print(f'Table has been updated for: {package_name}{version}')

       
    return signatures
    
# Verifies the signature with the pairs
def verify_signature(asc_url, pom_url):
    try:
        output = sb.check_output(["gpg", "--keyserver-option", "auto-key-retrieve", "--keyserver", "keyserver.ubuntu.com",
                                            "--verify", asc_url, pom_url], stderr=sb.STDOUT)
        return output.decode("utf-8")
    except sb.CalledProcessError as e:
        # print(f"Error verifying signature: {e}")
        return e.output
    

# Don't accept None as input, parse the string output of gpg into meaningful data values
def format_output(output):
    columns=['raw_output', 'signature_date', 'signature_key', 'request_key',
            'signature_validity', 'signature_trusted', 'signature_indication', 'primary_key_fingerprint']

    try:
        output = output.replace('\n: ', '').replace('\\n', '')
        output_list = output.split('gpg:')
        output_list = [item.strip() for item in output_list]
        # removes the first element, which is always ['b', ..]
        output_list = output_list[1:]
    
        # Split ['Signature made Mon Apr 11 16:23:30 2016 EDTusing RSA key 7F77D902717A5EAB', ...] 
        # -> Expected: ['Signature made Mon Apr 11 16:23:30 2016 EDT', 'RSA key 7F77D902717A5EAB']
        signature_date_n_key = output_list[0].split('using ')
        if len(signature_date_n_key) > 1:
            # RSA key ...
            output_list.insert(1, signature_date_n_key[1])
            # Split ['Signature made Mon Apr 11 16:23:30 2016 EDT'] -> Expected: ['Signature ', 'Mon Apr 11 16:23:30 2016 EDT']
            signature_date = signature_date_n_key[0].split('made ')
            if len(signature_date) > 1:
                output_list[0] = signature_date[1]
        # ['signature_date', 'signature_key', ...], truncate unnecessary string
        else:
            # Split ['Signature made Mon Apr 11 16:23:30 2016 EDT'] -> Expected: ['Signature ', 'Mon Apr 11 16:23:30 2016 EDT']
            signature_date = output_list[0].split('made ')
            if len(signature_date) > 1:
                output_list[0] = signature_date[1]
            # Split ['using RSA key 7F77D902717A5EAB'] -> Expected: ['', 'RSA key 7F77D902717A5EAB']
            signature_key = output_list[1].split('using ')
            if len(signature_key) > 1:
                output_list[1] = signature_key[1]
        
        # Check if key['signature_date', 'signature_key', '', 'signature_validity']
        if 'requesting key' not in output and 'issuer' not in output:
            output_list.insert(2, '')
            # else if key is requested, output_list = ['date', 'key', 'request_key', 'validity']

        # 'There is no indication that the signature belongs to the owner.\nPrimary key fingerprint: D6F1 BC78 6078 08EC 8E9F  6943 7A88 6094 4FAD 5F62']
        if 'Primary key fingerprint' in output:
            signature_indc_n_finger = output_list[-1].split('\n')

            if len(signature_indc_n_finger) > 1:
                output_list[-1] = signature_indc_n_finger[0]
                output_list.append(signature_indc_n_finger[1])
        # prepend the raw output
        output_list.insert(0, output)

        # Normal = 3
        # ['Signature made Mon Apr 11 16:23:30 2016 EDT', 'using RSA key 7F77D902717A5EAB', 
        # 'Can\'t check signature: No public key"']

        # Edge case = 4
        # ['Signature made Wed Feb  7 01:43:53 2018 EST', 'using DSA key A2115AE15F6B8B72', 
        # 'issuer "bodewig@apache.org"', "Can\\'t check signature: No public key'"]

        # Edge case = 4, requesting key from keyserver.ubuntu.com
        # ['Signature made Mon Feb 27 09:26:03 2023 EST', 'using EDDSA key DE8FD5826F9380467CBAF35F468C23190900DC54', 
        # 'requesting key 468C23190900DC54 from hkp://keyserver.ubuntu.com', 'Can\'t check signature: No public key"']
        
        # Edge case = 4
        # ['Thu May 31 14:56:56 2018 EDT', 'RSA key 353E41386ACD3CBED5B1C5DFBCB5D54D505C9A00', 'Good signature from "khatilov <alex@akex.cc>" [expired]', 
        # 'Note: This key has expired!\nPrimary key fingerprint: 353E 4138 6ACD 3CBE D5B1  C5DF BCB5 D54D 505C 9A00'

        # Normal = 6
        # 'Wed Jun 23 07:26:38 2010 EDT', 'RSA key 7A8860944FAD5F62', 
        # 'Good signature from "Sebastian Bazley (ASF CODE SIGNING KEY) <sebb@apache.org>" [unknown]', 
        # 'WARNING: This key is not certified with a trusted signature!', 
        # 'There is no indication that the signature belongs to the owner.', 
        # 'Primary key fingerprint: D6F1 BC78 6078 08EC 8E9F  6943 7A88 6094 4FAD 5F62']

    except Exception as e:
        return [output, e.args[0], '', '', '', '', '', '',]

    
    return output_list


            
# Recursive function to process the repository
def run_maven(repo_url):
    # We have reached the end of nested dir
    dirs = get_dirs(repo_url)
    if not dirs:
        download_files(repo_url)
        return
    # nested directories ahead
    for dir in dirs:
        run_maven(repo_url + dir)

# Divide the root_pkg directories by the specified batch_size
def divide_dirs(base_repo_url, batch_size):
    dirs = get_dirs(base_repo_url)
    list_dirs = []
    temp_dir = []
    for i in range(0, len(dirs), batch_size):
        if i + batch_size > len(dirs):
            temp_dir = dirs[i:len(dirs)]
        else:
            temp_dir = dirs[i:i+batch_size]
        list_dirs.append(temp_dir)
    
    return list_dirs
    
# generate tables in scratch space
def generate_dataset(list_dirs):

    global lib_name
    # ex) lists_dir = lists_dir[0] = ['HTTPClient/, abbot/', academy/, acegisecurity/]
    # dirs = [dir for dir in args]
    for dir in list_dirs:
        print(dir)
        # change path to /com after maven2/ when running individual dir
        run_maven(f'https://repo1.maven.org/maven2/{dir}')

# 2mil = 50gb
# 4mil = 100gb
# 3000000 files = 600GB -> Don't donwload files, just get the verification result



# Specified command line input is 0
if __name__ == "__main__":
    
    # list_dir = ['aws/']
    # Local testing
    # local = True
    
    parser = argparse.ArgumentParser()
    parser.add_argument('inputs', nargs='+')
    args = parser.parse_args()
    list_dirs = args.inputs


    # args = str(sys.argv[1:])
    # list_dirs = [arg for arg in args]
    # print(list_dirs)
    # with open('file.txt', 'a') as file:
    #     file.write(sys.argv[1])
    # print(list_dirs)
    generate_dataset(list_dirs)

