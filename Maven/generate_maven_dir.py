import requests as rq
from bs4 import BeautifulSoup
import csv
from bs4.element import NavigableString


maven_root_dir = 'https://repo1.maven.org/maven2/'
local_log_file_path = '/home/tschorle/Maven/file_structure2.csv'




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
        # dates = []
        # times = []
        
        # Find all a tags
        soup = BeautifulSoup(response.text, "html.parser")
        for a_tag in soup.find_all("a"):

            # if the href includes a forward slash the entry is another sub-dir
            href = a_tag.get("href")
            if '/' in href:
                dirs.append(href)
            else:
                files.append(href)


        # # extract dates for the files
        # pre = soup.body.main.pre.children
        # for p in pre:
        #     if isinstance(p, NavigableString):
        #         text = p.string.strip()
        #         if text is not '':
        #             split = text.split(' ')
        #             dates.append([0])
        #             times.append([1])


        # # if there is a mismatch make them empty
        # if len(files) != len(dates) or len(files) != len(times):
        #     dates = []
        #     times = []

        # Don't include the ../ dirs[0] (previous directory)
        # return dirs[1:], files, dates, times
        return dirs[1:], files
    
    # If we didn't, return an empty list and print out the url
    else:
        print(f'No response from {repo_url}')
        return [], []
    

def generate_file_structure(repo_url, logger):
    """
    Takes a given url and generates entries in a csv which correspond to the
    files that exist in the maven repository.
    
    repo_url: the base url to generate the csv from.

    logger: the csv writer to write with.
    """

    # get all the files and subdirectories in this directory
    # dirs, files, dates, times = get_dirs_files(repo_url=repo_url)
    dirs, files = get_dirs_files(repo_url=repo_url)

    # check if this directory is completely empty - if so log it
    if not dirs and not files:
        logger.writerow([repo_url, 'EMPTY_DIR', ''])

    # otherwise, log the files and dig deeper
    else:

        for f in files:
            logger.writerow([repo_url, 'FILE', f])

        for dir in dirs:
            generate_file_structure(repo_url=(repo_url+dir), logger=logger)



with open(local_log_file_path, 'a', newline='') as log_file:

    logger = csv.writer(log_file)
    generate_file_structure(maven_root_dir, logger=logger)