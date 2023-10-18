#!/usr/bin/env python

# Imports
import argparse
from datetime import datetime
import json
import numpy as np
import matplotlib.pyplot as plt
from util.files import valid_path_create, valid_path

# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'


def trunc_datetime(someDate):
    return someDate.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


months = [
    (datetime(2017, 9, 1), 0),
    (datetime(2017, 10, 1), 1),
    (datetime(2017, 11, 1), 2),
    (datetime(2017, 12, 1), 3),
    (datetime(2018, 1, 1), 4),
    (datetime(2018, 2, 1), 5),
    (datetime(2018, 3, 1), 6),  # middle
    (datetime(2018, 4, 1), 7),
    (datetime(2018, 5, 1), 8),
    (datetime(2018, 6, 1), 9),
    (datetime(2018, 7, 1), 10),
    (datetime(2018, 8, 1), 11),
    (datetime(2018, 9, 1), 12),
]

maven_time = []
pypi_time = []
npm_time = []
huggingface_time = []
docker_time = []


def get_bucket(date):
    for i, (month, index) in enumerate(months):
        if date == month:
            return i
    return None


def pypi(args):
    '''This function is used to analyze the adoption of PyPI.

    args: The arguments passed in from the command line.
    '''

    # Normalize paths
    input_file = valid_path(
        args.input_file.replace('-reg-', 'pypi'))

    def from_str(s):
        try:
            s = s[:19]
            date = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
            return trunc_datetime(date)
        except:
            return None

    # init the time array
    for i in range(13):
        pypi_time.append({
            'total_units': 0,
            'total_signatures': 0,
            'total_unsigned': 0,
        })

    # open the input file
    with open(input_file, 'r') as f:
        # iterate through the file
        for line in f:
            # load the line as a json object
            package = json.loads(line)

            for version_name, files in package['versions'].items():
                indx = get_bucket(from_str(files[0]['upload_time']))
                if indx is None:
                    continue

                for file in files:
                    pypi_time[indx]['total_units'] += 1

                    if file['has_signature'] and file['signature'] is not None:
                        pypi_time[indx]['total_signatures'] += 1

                    else:
                        pypi_time[indx]['total_unsigned'] += 1


def maven(args):
    '''This function is used to analyze the adoption of Maven.

    args: The arguments passed in from the command line.
    '''
    # Normalize paths
    input_file = valid_path(
        args.input_file.replace('-reg-', 'maven'))

    def from_str(s):
        date = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
        return trunc_datetime(date)

    # init the time array
    for i in range(13):
        maven_time.append({
            'total_units': 0,
            'total_signatures': 0,
            'total_unsigned': 0,
        })

    # open the input file
    with open(input_file, 'r') as f:
        # iterate through the file
        for line in f:
            # load the line as a json object
            package = json.loads(line)

            # increment the total versions

            for version in package['versions']:

                indx = get_bucket(from_str(version['published_at']))
                if indx is None:
                    continue

                if 'files' in version:
                    for file in version['files']:
                        maven_time[indx]['total_units'] += 1

                        if file['has_signature'] \
                                and file['stderr'] is not None \
                                and file['stderr'] != '':
                            maven_time[indx]['total_signatures'] += 1

                        else:
                            maven_time[indx]['total_unsigned'] += 1


def npm(args):
    '''This function is used to analyze the adoption of npm.

    args: The arguments passed in from the command line.
    '''
    # Normalize paths
    input_file = valid_path(
        args.input_file.replace('-reg-', 'npm'))

    def from_str(s):
        try:
            s = s[:19]
            date = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
            return trunc_datetime(date)
        except:
            return None

    # init the time array
    for i in range(13):
        npm_time.append({
            'total_units': 0,
            'total_signatures': 0,
            'total_unsigned': 0,
        })

    # open the input file
    with open(input_file, 'r') as f:

        for line in f:

            package = json.loads(line)

            # iterate through the versions
            for version in package['versions']:

                if 'signatures' not in version:
                    continue
                indx = get_bucket(from_str(version['published_at']))
                if indx is None:
                    continue

                npm_time[indx]['total_units'] += 1

                signatures = version['signatures']

                if signatures is None or (
                        signatures['ecdsa'] is None and signatures['pgp'] is None):
                    npm_time[indx]['total_unsigned'] += 1
                    continue
                if signatures['pgp'] is not None:
                    npm_time[indx]['total_signatures'] += 1


def huggingface(args):
    '''This function is used to analyze the adoption of HuggingFace.

    args: The arguments passed in from the command line.
    '''
    # Normalize paths
    input_file = valid_path(
        args.input_file.replace('-reg-', 'huggingface'))

    def from_str(s):
        date = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
        return trunc_datetime(date)

    # init the time array
    for i in range(13):
        huggingface_time.append({
            'total_units': 0,
            'total_signatures': 0,
            'total_unsigned': 0,
        })

    # open the input file
    with open(input_file, 'r') as f:
        # iterate through the file
        for line in f:
            # load the line as a json object
            package = json.loads(line)


            for commit in package['commits']:
                indx = get_bucket(from_str(commit['time']))
                if indx is None:
                    continue

                huggingface_time[indx]['total_units'] += 1

                if commit['output'] == '' and commit['error'] == '':
                    huggingface_time[indx]['total_unsigned'] += 1
                else:
                    huggingface_time[indx]['total_signatures'] += 1


def docker(args):
    '''This function is used to analyze the adoption of Docker.

    args: The arguments passed in from the command line.
    '''
    # Normalize paths
    input_file = valid_path(
        args.input_file.replace('-reg-', 'docker'))

    def from_str(s):
        try:
            s = s[:19]
            date = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
            return trunc_datetime(date)
        except:
            return None

    # init the time array
    for i in range(13):
        docker_time.append({
            'total_units': 0,
            'total_signatures': 0,
            'total_unsigned': 0,
        })

    # open the input file
    with open(input_file, 'r') as f:
        # iterate through the file
        for line in f:
            # load the line as a json object
            package = json.loads(line)

            for version in package['versions']:
                indx = get_bucket(from_str(version['published_at']))
                if indx is None:
                    continue

                docker_time[indx]['total_units'] += 1

                if len(package['signatures']) != 0:
                    if version['number'] in [tag['SignedTag'] for tag in package['signatures'][0]['SignedTags']]:
                        print('hit')
                        docker_time[indx]['total_signatures'] += 1
                        continue
                docker_time[indx]['total_unsigned'] += 1


# Function to parse arguments
def parse_args():
    ''' This function parses arguments passed to the script.

    returns: the arguments passed to the script.
    '''

    # Create parser
    parser = argparse.ArgumentParser(
        description='This script is used to analyze the adoption of all '
        'registries with data. The script takes in the ndjson file of '
        'adoption data and outputs a summary json file.')

    # global arguments
    parser.add_argument('--input-file',
                        type=str,
                        default='./data/-reg-/adoption.ndjson',
                        help='The name of the input file for the registry. '
                        'Defaults to <./data/-reg-/adoption.ndjson>. '
                        'The -reg- will be replaced with the registry name.')
    parser.add_argument('--output-file',
                        type=str,
                        default='./data/-reg-/timeline.json',
                        dest='summary',
                        help='The name of the summary file for the registry. '
                        'Defaults to <./data/-reg-/timeline.json>. '
                        'The -reg- will be replaced with the registry name.')

    args = parser.parse_args()

    return args


def main():
    '''
    This is the main function of the script.
    '''
    # Parse arguments
    args = parse_args()

    # Run appropriate analysis
    #maven(args)
    #print(maven_time)
    #npm(args)
    #print(npm_time)
    #pypi(args)
    #print(pypi_time)
    #huggingface(args)
    #print(huggingface_time)
    docker(args)
    print(docker_time)


    maven_time = [{'total_units': 3220, 'total_signatures': 3014, 'total_unsigned': 206}, {'total_units': 2683, 'total_signatures': 2461, 'total_unsigned': 222}, {'total_units': 2561, 'total_signatures': 2480, 'total_unsigned': 81}, {'total_units': 2512, 'total_signatures': 2400, 'total_unsigned': 112}, {'total_units': 2828, 'total_signatures': 2710, 'total_unsigned': 118}, {'total_units': 3086, 'total_signatures': 2938, 'total_unsigned': 148}, {'total_units': 3009, 'total_signatures': 2875, 'total_unsigned': 134}, {'total_units': 2607, 'total_signatures': 2484, 'total_unsigned': 123}, {'total_units': 2926, 'total_signatures': 2704, 'total_unsigned': 222}, {'total_units': 2766, 'total_signatures': 2691, 'total_unsigned': 75}, {'total_units': 3233, 'total_signatures': 3022, 'total_unsigned': 211}, {'total_units': 3402, 'total_signatures': 3108, 'total_unsigned': 294}, {'total_units': 3238, 'total_signatures': 3021, 'total_unsigned': 217}]

    npm_time = [{'total_units': 27063, 'total_signatures': 5, 'total_unsigned': 0}, {'total_units': 29467, 'total_signatures': 11, 'total_unsigned': 0}, {'total_units': 31528, 'total_signatures': 12, 'total_unsigned': 0}, {'total_units': 27324, 'total_signatures': 3, 'total_unsigned': 0}, {'total_units': 34170, 'total_signatures': 7, 'total_unsigned': 0}, {'total_units': 31299, 'total_signatures': 8, 'total_unsigned': 0}, {'total_units': 36805, 'total_signatures': 18, 'total_unsigned': 0}, {'total_units': 35790, 'total_signatures': 19794, 'total_unsigned': 0}, {'total_units': 40147, 'total_signatures': 40147, 'total_unsigned': 0}, {'total_units': 39433, 'total_signatures': 33035, 'total_unsigned': 0}, {'total_units': 42689, 'total_signatures': 31878, 'total_unsigned': 0}, {'total_units': 45812, 'total_signatures': 44706, 'total_unsigned': 0}, {'total_units': 44012, 'total_signatures': 44012, 'total_unsigned': 0}]


    pypi_time = [{'total_units': 34104, 'total_signatures': 1739, 'total_unsigned': 32365}, {'total_units': 34944, 'total_signatures': 2034, 'total_unsigned': 32910}, {'total_units': 36095, 'total_signatures': 1757, 'total_unsigned': 34338}, {'total_units': 32004, 'total_signatures': 1350, 'total_unsigned': 30654}, {'total_units': 36995, 'total_signatures': 1599, 'total_unsigned': 35396}, {'total_units': 36642, 'total_signatures': 1714, 'total_unsigned': 34928}, {'total_units': 43165, 'total_signatures': 2218, 'total_unsigned': 40947}, {'total_units': 45716, 'total_signatures': 2153, 'total_unsigned': 43563}, {'total_units': 42506, 'total_signatures': 1951, 'total_unsigned': 40555}, {'total_units': 46438, 'total_signatures': 1530, 'total_unsigned': 44908}, {'total_units': 46868, 'total_signatures': 1421, 'total_unsigned': 45447}, {'total_units': 49364, 'total_signatures': 1343, 'total_unsigned': 48021}, {'total_units': 46310, 'total_signatures': 1136, 'total_unsigned': 45174}]



    mv = [bucket['total_signatures']/bucket['total_units'] for bucket in maven_time]
    np = [bucket['total_signatures']/bucket['total_units'] for bucket in npm_time]
    pp = [bucket['total_signatures']/bucket['total_units'] for bucket in pypi_time]
    dc = [bucket['total_signatures']/bucket['total_units'] for bucket in docker_time]

    mv = np.array(mv)
    np = np.array(np)
    pp = np.array(pp)
    dc = np.array(dc)

    mv = mv / mv[6]
    np = np / np[6]
    pp = pp / pp[6]
    dc = dc / dc[6]

    plt.plot(mv, label='Maven')
    plt.plot(np, label='npm')
    plt.plot(pp, label='PyPI')
    plt.plot(dc, label='Docker')

    plt.axvline(x=6, color='k', linestyle='--', label='Change in PyPI')

    plt.xlabel('Months')
    plt.ylabel('Normalized Adoption')
    plt.title('Adoption of Software Signing')

    plt.legend()
    plt.show()


# Classic Python main function
if __name__ == '__main__':
    main()  # Call main function
