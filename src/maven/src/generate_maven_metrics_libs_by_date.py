import os
import csv
import pandas as pd
from datetime import datetime

# Fifth file to run
"""
Generate metrics table for libs that lies in certain date range provided by the user
"""

# Dates
# 11 AUG 2015
# 22 MAR 2018
# 26 OCT 2022
# 23 MAY 2023
# Present

date_range = '2015-08-11'
scratch_space = f'../data/outputs/libs/'

def generate_maven_dict(lib):
    """
    Generate dictionary with key as path to file location in Maven Central

    lib: library to process

    returns: dictionary with keys as path to file location in Maven Central
    """

    maven_file = f'../data/maven_dirs{lib}.csv'
    maven_dict = {}

    with open(maven_file, 'r', newline='') as maven:
        
        maven_reader = csv.reader(maven)
            
        for row in maven_reader:
            maven_dict[f'{row[0]}{row[2]}'] = row[3]
        
    maven.close()
    return maven_dict



def is_in_date_range(maven_dict, row, date_range):
    """
    Checks whether a file falls within date_range

    maven_dict: dictionary with keys as path to file location in Maven Central

    row: current row from the table

    date_range: files published before date_range is counted

    returns: True or False whether the file is published before date_range
    """
    
    maven_date = maven_dict[f'{row[0]}{row[1]}']

    date_range = datetime.strptime(date_range, '%Y-%m-%d')
    maven_date = datetime.strptime(maven_date, '%Y-%m-%d')
    
    if maven_date <= date_range:
        return True
    return False


def get_metrics_no_signs(lib, maven_dict, date_range):
    """
    Counts up the number of files without a paired signature files in date_range

    lib: library to process
    
    maven_dict: dictionary with keys as path to file location in Maven Central

    date_range: files published before date_range is counted

    returns: the number of files without a paired signature files in date_range
    """
    
    invalid_table = f'../data/no_signs/no_signs_libs.csv'
    count = 0
    
    with open(invalid_table, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            curr_lib = row[0].split('/')[4]
            if is_in_date_range(maven_dict, row, date_range) and curr_lib == lib:
                count+=1
    file.close()

    return count

 
def get_metrics(table, keys, libs, ind, maven_dict, date_range):
    """
    Create a table with counts of which criteria the verification result lies in

    table: table to process

    keys: list of keys used to verify the signature
    
    maven_dict: dictionary with keys as path to file location in Maven Central

    date_range: files published before date_range is counted

    returns: dictionary containing the counts
    """
    is_first = False
    if '_0.csv' in table:
        is_first = True

    total_entries = 0
    num_goods = 0
    num_goods_key_expired = 0
    num_goods_no_pub_key = 0
    num_bads = 0
    num_bads_key_expired = 0
    num_bads_no_pub_key = 0
    num_unverifiable = 0
    num_unverifiable_key_expired = 0
    num_unverifiable_no_pub_key = 0


    with open(f'{scratch_space}tables/{table}', 'r', newline='') as file:
        csv_reader = csv.reader(file)
        curr_lib = ''
        row_counter = 0
        for i, row in enumerate(csv_reader):
            # Ignore the first entry of tables to prevent overlapping entries 
            if not is_first and i == 0:
                continue
            if i >= ind:
                lib = row[0].split('/')[4]
                # Start processing a lib
                if not curr_lib:
                    curr_lib = lib
                # Continuously process curr_lib until next library detected/current table finishes
                elif curr_lib == lib:
                    pass
                # New lib detected, write the current lib to a file
                else:
                    # print('libs: ' + str(libs))
                    print('curr_lib: ' + curr_lib)
                    print('Stopped at the new library: ' + lib)
                    break
                
                # Add features to collect from output table
                if is_in_date_range(maven_dict, row, date_range):
                    if 'key ID' in row[2]:
                        key_ind = row[2].find('key ID')
                        local_key = row[2][key_ind+7:key_ind+15]
                        if not local_key in keys:
                            keys.append(local_key)
                    if 'Good signature' in row[2]:
                        num_goods+=1
                        if 'expired' in row[2]: num_goods_key_expired+=1
                        if 'No public key' in row[2]: num_goods_no_pub_key+=1
                            # print(row[2])
                    elif 'BAD signature' in row[2]:
                        # print(row[2])
                        num_bads+=1
                        if 'expired' in row[2]: num_bads_key_expired+=1
                        if 'No public key' in row[2]: num_bads_no_pub_key+=1
                    else:
                        num_unverifiable+=1
                        if 'expired' in row[2]: num_unverifiable_key_expired+=1
                        if 'No public key' in row[2]: num_unverifiable_no_pub_key+=1
                    total_entries+=1
                row_counter+=1
        file.close()
        libs.append(curr_lib)
        # print(f'Last item from curr_lib was: {row[1]}')
        ind += row_counter
        # print('ind: ' + str(ind))
        total_key_expired = num_goods_key_expired+num_bads_key_expired+num_unverifiable_key_expired
        total_no_pub_key = num_goods_no_pub_key+num_bads_no_pub_key+num_unverifiable_no_pub_key
        
    return {'lib': curr_lib, 'total_entries': total_entries, 'num_goods':num_goods, 'num_bads':num_bads, 'num_unverifiables':num_unverifiable,
            'num_keys_used': len(keys), 'total_key_expired':total_key_expired, 'num_goods_key_expired':num_goods_key_expired, 
            'num_bads_key_expired':num_bads_key_expired, 'num_unverifiables_key_expired':num_unverifiable_key_expired,
            'total_no_pub_key':total_no_pub_key, 'num_goods_no_pub_key':num_goods_no_pub_key, 
            'num_bads_no_pub_key':num_bads_no_pub_key, 'num_unverifiables_no_pub_key':num_unverifiable_no_pub_key}, libs, ind
            


def compute_metrics(global_row, global_keys, maven_dict, date_range):
    """
    Formats the counted values, generate a table

    global_row: dictionary containing the counts

    global_keys: total keys used to verify signatures in a single library

    maven_dict: dictionary with keys as path to file location in Maven Central

    date_range: files published before date_range is counted
    """
    lib = global_row['lib']

    os.makedirs(f'{scratch_space}/metrics/{date_range}/', exist_ok=True)
    metrics_path = f'{scratch_space}/metrics/{date_range}/{lib}_{date_range}_metrics.csv'
    no_signs = get_metrics_no_signs(lib, maven_dict, date_range)

    with open(metrics_path, 'a', newline='') as metrics_file:
    
        csv_writer = csv.writer(metrics_file)

        ratio_goods = "{:.2f}".format(float(global_row['num_goods']) / global_row['total_entries'] * 100 if global_row['total_entries'] !=0 else float(0.00))
        ratio_bads = "{:.2f}".format(float(global_row['num_bads']) / float(global_row['total_entries']) * 100 if global_row['total_entries'] !=0 else float(0.00))
        ratio_unverifiables = "{:.2f}".format(float(global_row['num_unverifiables']) / float(global_row['total_entries']) * 100 if global_row['total_entries'] !=0 else float(0.00))
        
        ratio_goods_key_expired = "{:.2f}".format(float(global_row['num_goods_key_expired']) / float(global_row['total_key_expired']) * 100 if global_row['total_key_expired'] !=0 else float(0.00))
        ratio_bads_key_expired = "{:.2f}".format(float(global_row['num_bads_key_expired']) / float(global_row['total_key_expired']) * 100 if global_row['total_key_expired'] !=0 else float(0.00))
        ratio_unverifiables_key_expired = "{:.2f}".format(float(global_row['num_unverifiables_key_expired']) / float(global_row['total_key_expired']) * 100 if global_row['total_key_expired'] !=0 else float(0.00))
        
        ratio_goods_no_pub_key = "{:.2f}".format(float(global_row['num_goods_no_pub_key']) / float(global_row['total_no_pub_key']) * 100 if global_row['total_no_pub_key'] !=0 else float(0.00))
        ratio_bads_no_pub_key = "{:.2f}".format(float(global_row['num_bads_key_expired']) / float(global_row['total_no_pub_key']) * 100 if global_row['total_no_pub_key'] !=0 else float(0.00))
        ratio_unverifiables_no_pub_key = "{:.2f}".format(float(global_row['num_unverifiables_key_expired']) / float(global_row['total_no_pub_key']) * 100 if global_row['total_no_pub_key'] !=0 else float(0.00))

        keys = ['total_entries', 'num_goods', 'num_bads', 'num_unverifiables', 'ratio_goods', 'ratio_bads',\
                        'ratio_unverifiables', 'num_keys_used', 'total_key_expired', 'num_goods_key_expired', 'num_bads_key_expired', \
                        'num_unverifiables_key_expired', 'ratio_goods_key_expired', 'ratio_bads_key_expired', 'ratio_unverifiables_key_expired',\
                            'total_no_pub_key', 'num_goods_no_pub_key', 'num_bads_no_pub_key', 'num_unverifiables_no_pub_key', 'ratio_goods_no_pub_key',\
                            'ratio_bads_no_pub_key', 'ratio_unverifiables_no_pub_key', 'no_signs']
        
        global_row['total_entries'] += no_signs
        global_row['num_unverifiables'] += no_signs
        values = [global_row['total_entries'], global_row['num_goods'], global_row['num_bads'], global_row['num_unverifiables'], ratio_goods, 
                ratio_bads, ratio_unverifiables, len(global_keys), global_row['total_key_expired'], global_row['num_goods_key_expired'], 
                global_row['num_bads_key_expired'], global_row['num_unverifiables_key_expired'], ratio_goods_key_expired, ratio_bads_key_expired,
                ratio_unverifiables_key_expired, global_row['total_no_pub_key'], global_row['num_goods_no_pub_key'], global_row['num_bads_no_pub_key'],
                global_row['num_unverifiables_no_pub_key'], ratio_goods_no_pub_key, ratio_bads_no_pub_key, ratio_unverifiables_no_pub_key, no_signs]


        # Generate a final row to write to file
        final_row = {}
        for key in keys:
            for value in values:
                final_row[key] = value
                values.remove(value)
                break
        print('************ Final row to write to file ************')
        print(f'{lib} - {final_row}')
        csv_writer.writerow(list(final_row.keys()))
        csv_writer.writerow(list(final_row.values()))

    metrics_file.close()

def sortby(x):
    """
    Sorts the table by numerical order
    """
    return int(x.split('_')[2].split('.')[0])

def sign_file_last(file_path):
    """
    Gets the last entry from last table of a library
    """
    end_index = 0
    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)  # Read all rows and store them in a list
        print(f'Sign file last item at {len(rows)-1} - {rows[len(rows)-1][:2]}')
        end_index = len(rows)-1
    csvfile.close()
    return end_index


def compute_metrics_libs(date_range):
    """
    Formats the counted values, generate a table for libraries that has signatures

    date_range: files published before date_range is counted
    """
    lib = 'libs'
    tables = os.listdir(f'../data/outputs/libs/tables/')
    tables.sort(key=sortby)
    global_keys = []
    # locally itereating through libs
    libs = []

    maven_dict = generate_maven_dict(lib)

    sign_path = f'../data/signs/signs_libs.csv'
    last_table_ind = sign_file_last(sign_path)


    for i, table in enumerate(tables):
        global_ind = int(tables[i].split('_')[2].split('.')[0])
        ind = 0
        # Process the last table
        if i == len(tables)-1:
            while global_ind+ind+1 < last_table_ind:
                global_keys = []
                # ind is to keep track of where to re-start from the current table until it finishes processing
                new_row, libs, ind = get_metrics(table, global_keys, libs, ind, maven_dict, date_range)
                compute_metrics(new_row, global_keys, maven_dict, date_range)
                # print(new_row)
                # print(libs)
        else:
            # Continue to process 1 table until it reaches the end of the file
            while global_ind+ind+1 < int(tables[i+1].split('_')[2].split('.')[0]):
                global_keys = []
                new_row, libs, ind = get_metrics(table, global_keys, libs, ind, maven_dict, date_range)
                compute_metrics(new_row, global_keys, maven_dict, date_range)
                # print(new_row)
                # print(libs)
        # print(f"end of {table}, last lib was {new_row['lib']}")
        # print(libs)


def compute_metrics_no_sign_libs(date_range):
    """
    Formats the counted values, generate a table for libraries that 
    do not have any signs (HTTPClient/, acegisecurity/, etc)

    date_range: files published before date_range is counted
    """
    invalid_table = f'../data/no_signs/no_signs_libs.csv'
    valid_libs = [lib.split('_')[0] for lib in os.listdir(f'{scratch_space}/metrics/{date_range}')]
    processed_libs = []
    maven_dict = generate_maven_dict('libs')
    with open(invalid_table, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            lib = row[0].split('/')[4]
            if lib not in valid_libs and lib not in processed_libs:
                keys = []
                row = {'lib': lib, 'total_entries': 0, 'num_goods':0, 'num_bads':0, 'num_unverifiables':0, 'num_keys_used': len(keys),
                        'total_key_expired':0, 'num_goods_key_expired':0, 'num_bads_key_expired':0, 'num_unverifiables_key_expired':0,
                        'total_no_pub_key':0, 'num_goods_no_pub_key':0, 'num_bads_no_pub_key':0, 'num_unverifiables_no_pub_key':0}
                compute_metrics(row, keys, maven_dict, date_range)
                processed_libs.append(lib)
    file.close()

if __name__ == '__main__':
    """
    After the run, there should be {lib}_{date_range}_metrics.csv in {scratch_space}/metrics/{date_range}/
    All other libraries will be stored under libs/
    """ 
    compute_metrics_libs(date_range)
    compute_metrics_no_sign_libs(date_range)
