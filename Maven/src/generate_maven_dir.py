import requests as rq
from bs4 import BeautifulSoup
import csv
import os
import pandas as pd

# First file to run:
"""
Place all files from Maven repository by their main directory names 'lib'
"""

def get_dirs_files(repo_url):
    """
    Get all the sub directories from the provided url.

    repo_url: the base url to search from.

    returns: Two values, the first is a list of the subdirectories and the
    second is a list of files in the given url.
    """
    
    # Get the html from the given url
    response = rq.get(repo_url)
    
    # Check to see if we got a response
    if response:
        
        dirs = []
        files = []
        dates = []
        times = []
        sizes = []

        # Find all a tags
        soup = BeautifulSoup(response.text, "html.parser")
        for a_tag in soup.find_all("a"):

            # if the href includes a forward slash the entry is another sub-dir
            href = a_tag.get("href")
            if '/' in href:
                dirs.append(href)
            else:
                files.append(href)

        pre_tag = soup.find("pre")

        # Everything is nested inside <pre>
        for i, item in enumerate(pre_tag):
            # Target the lines outside of <a>
            if i % 2 == 0:
                # Turn the line into a list: ["2005-05-19", "05:44", ...., "302"]
                dts = str(item).strip().split(' ')
                dts = [item for item in dts if item]
                date = ''
                time = ''
                size = ''
                # Ignore empty structures
                if len(dts) >= 2:
                    # Edge case when size is too big and merges with time - ['2022-02-03', '14:251035358090']
                    if len(dts) == 2:
                        if len(dts[0]) > 1: date = dts[0]
                        if len(dts[1]) > 1: time = dts[1][:5]
                        size = dts[1][5:]
                    elif len(dts) == 3:
                        if len(dts[0]) > 1: date = dts[0]
                        if len(dts[1]) > 1: time = dts[1]
                        if len(dts[-1]) > 1: size = dts[-1]
                    dates.append(date)
                    times.append(time)
                    sizes.append(size)

        # Don't include the ../ dirs[0] (previous directory)
        # return dirs[1:], files, dates, times
        return dirs[1:], files, dates, times, sizes
    
    # If we didn't, return an empty list and print out the url
    else:
        print(f'No response from {repo_url}')
        return [], [], [], [], []
    

def generate_file_structure(repo_url, logger):
    """
    Takes a given url and generates entries in a csv which correspond to the
    files that exist in the maven repository.
    
    repo_url: the base url to generate the csv from.

    logger: the csv writer to write with.
    """
    
    # get all the files and subdirectories in this directory
    dirs, files, dates, times, sizes = get_dirs_files(repo_url=repo_url)
    
    # check if this directory is completely empty - if so log it
    if not dirs and not files:
        logger.writerow([repo_url, 'EMPTY_DIR', '', '', '', ''])
    
    # otherwise, log the files and dig deeper
    else:
        ind_to_start = len(dirs)
        for i, f in enumerate(files, ind_to_start):
            if dates:
                logger.writerow([repo_url, 'FILE', f, dates[i], times[i], sizes[i]])

        for dir in dirs:
            generate_file_structure(repo_url=(repo_url+dir), logger=logger)
    

if __name__ == "__main__":
    """
    After the run of Step 1, there should be {lib}.csv file existing in local_log_file_path
    After the run of Step 2, there should be from libs_0.csv to libs_11.csv in local_log_file_path/libs/
    """

    # Step 1. Run one by one with different jobs for parallel processing
    # [aws, com, dev, io, libs, net, org, software]
    lib = 'aws/'
    maven_root_dir = f'https://repo1.maven.org/maven2/{lib}'
    # Change the target path as necessary
    local_log_file_path = '../data/maven_dirs/'

    # Create a directory to place the file
    os.makedirs(local_log_file_path, exist_ok=True)
    
    local_log_file_path += f'{lib[:-1]}.csv'
    with open(local_log_file_path, 'a', newline='') as log_file:
        logger = csv.writer(log_file)
        generate_file_structure(maven_root_dir, logger=logger)
    log_file.close()

    # Step 2. Run the rest of directories, consider them as one library, 'libs'
    other_dirs_path = 'libs/other_dirs.txt'
    with open(other_dirs_path, 'r') as other_dirs_file:
        lib_count = 0
        other_dirs = []
        for line in other_dirs_file:
            dirs = line.split(' ')
            for dir in dirs:
                print(f'Processing {dir}')
                maven_root_dir = f'https://repo1.maven.org/maven2/{dir}'
                local_log_file_path = '../data/maven_dirs/libs.csv'
                with open(f'{local_log_file_path}', 'a', newline='') as log_file:
                    logger = csv.writer(log_file)
                    generate_file_structure(maven_root_dir, logger=logger)
                log_file.close()
            lib_count+=1
    
