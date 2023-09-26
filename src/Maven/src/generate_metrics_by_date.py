import os
import csv
import pandas as pd
import time
from datetime import datetime

# Fifth file to run
"""
Generate metrics table that lies in certain date range provided by the user
"""

# Dates
# 11 AUG 2015
# 22 MAR 2018
# 26 OCT 2022
# 23 MAY 2023
# Present

lib = 'aws'
date_range = '2018-03-22'
scratch_space = f'../data/outputs/{lib}/'


def generate_maven_dict(lib, table, date_range):
    """
    Generate dictionary that falls within the date range provided

    lib: library to process

    table: table from library

    date_range: files published before date_range is counted

    returns: dictionary with keys as path to file location in Maven Central
    """

    start_time = time.perf_counter()
    date_to = datetime.strptime(date_range, '%Y-%m-%d')
    table_path = f'../data/outputs/{lib}/tables/{table}'
    maven_path = f'../data/outputs/{lib}.csv'
    maven_dict = {}
    len_maven_entries = 0
    no_date = 0
    
    # Other than the first table of the library contains overlap entry
    is_first = True
    if not '_0.csv' in table:
       is_first = False

    # Generate dictionary for each partial output table
    with open(table_path, 'r', newline='') as table_file:
        table_reader = csv.reader(table_file)
        
        for i, row in enumerate(table_reader):
            # Only the first table ignores this statement to count everything
            if not is_first and i == 0:
                continue
            maven_dict[f'{row[0]}{row[1]}'] = '.'
        # Counter to stop reading the maven file
        len_maven_entries = len(maven_dict)
    table_file.close()
    
    with open(maven_path, 'r', newline='') as maven_file:
        maven_reader = csv.reader(maven_file)
        entry_counter = 0
        out_of_range_counter = 0
        for i, row in enumerate(maven_reader):
            # len_maven_entries is always 1 greater than entry_counter+no_date except the first table (_0.csv)
            if entry_counter + out_of_range_counter + no_date == len_maven_entries:
                break
            maven_entry = f'{row[0]}{row[2]}'
            # Only target maven_entrys collected from the table
            try:
                if maven_dict[maven_entry]:
                    # When the entry doesn't have date from Maven central
                    if row[3]:
                        maven_date = datetime.strptime(row[3], '%Y-%m-%d')
                        if maven_date <= date_to:
                            maven_dict[maven_entry] = row[3]
                            entry_counter+=1
                        else:
                            out_of_range_counter+=1
                    else:
                        no_date+=1
            except:
                pass
    maven_file.close()
    
    end_time = time.perf_counter()
    # Calculate elapsed time
    elapsed_time = end_time - start_time
    print('******************generate_maven_dict******************')
    print("Elapsed time: ", elapsed_time)
    print(f'Total entries: {len(maven_dict)}')
    print(f'within range: {entry_counter}')
    print(f'out of range: {out_of_range_counter}')

    print(f'{next(iter(maven_dict))}, {maven_dict[next(iter(maven_dict))]}')
    
    return maven_dict

# Check whether the row falls within the date_range provided
def is_in_date_range(maven_dict, row):
    """
    Checks whether a file falls within date_range

    maven_dict: dictionary with keys as path to file location in Maven Central

    row: current row from the table

    returns: True or False whether the file is published before date_range
    """
    maven_entry = f'{row[0]}{row[1]}'
    try:
        maven_date = maven_dict[maven_entry]
        # Date is not within the range
        if maven_date == '.':
            return False
    except:
        return False

    return True

# Return number of no_sign falles within the date range
def get_metrics_no_signs(lib, date_range):
    """
    Counts up the number of files without a paired signature files in date_range

    lib: library to process

    date_range: files published before date_range is counted

    returns: the number of files without a paired signature files in date_range
    """
    date_to = datetime.strptime(date_range, '%Y-%m-%d')
    maven_path = f'../data/maven_dirs{lib}.csv'
    maven_dict = {}
    len_maven_entries = 0
    no_date = 0

    invalid_table = f'../data/no_signs/no_signs_{lib}.csv'

    with open(invalid_table, 'r', newline='') as invalid_file:
        invalid_reader = csv.reader(invalid_file)
        for row in invalid_reader:
            maven_dict[f'{row[0]}{row[1]}'] = '.'
        # Counter to stop reading the maven file
        len_maven_entries = len(maven_dict)
    invalid_file.close()
    
    print(f'len_maven_entries: {len_maven_entries}')
    with open(maven_path, 'r', newline='') as maven_file:
        maven_reader = csv.reader(maven_file)
        entry_counter = 0
        out_of_range_counter = 0
        for i, row in enumerate(maven_reader):
            # len_maven_entries is always 1 greater than entry_counter+no_date except the first table (_0.csv)
            if entry_counter + out_of_range_counter + no_date == len_maven_entries:
                break
            maven_entry = f'{row[0]}{row[2]}'
            # Only target maven_entrys collected from the table
            try:
                if maven_dict[maven_entry]:
                    # When the entry doesn't have date from Maven central
                    if row[3]:
                        maven_date = datetime.strptime(row[3], '%Y-%m-%d')
                        if maven_date <= date_to:
                            entry_counter+=1
                        else:
                            out_of_range_counter+=1
                    else:
                        no_date+=1
            except:
                pass
    print('******************get_metrics_no_signs******************')
    print(f'Total entries: {len(maven_dict)}')
    print(f'within range: {entry_counter}')
    print(f'out of range: {out_of_range_counter}')
    print(f'no_date: {no_date}')

    print(f'{next(iter(maven_dict))}, {maven_dict[next(iter(maven_dict))]}')

    del maven_dict
    
    return entry_counter

def get_metrics(table, keys, maven_dict):
    """
    Create a table with counts of which criteria the verification result lies in

    table: table to process

    keys: list of keys used to verify the signature
    
    maven_dict: dictionary with keys as path to file location in Maven Central

    returns: dictionary containing the counts
    """
    is_first = True

    if not '_0.csv' in table:
       is_first = False

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

    with open(f'{scratch_space}/tables/{table}', 'r', newline='') as file:
        
        csv_reader = csv.reader(file)
        
        for i, row in enumerate(csv_reader):
            # Take take care of duplicate entry in the table (previous last entry == current first entry)
            if not is_first and i == 0:
                continue
            # Count only if lies in certain date range
            if is_in_date_range(maven_dict, row):
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
                    num_bads+=1
                    if 'expired' in row[2]: num_bads_key_expired+=1
                    if 'No public key' in row[2]: num_bads_no_pub_key+=1
                else:
                    num_unverifiable+=1
                    if 'expired' in row[2]: num_unverifiable_key_expired+=1
                    if 'No public key' in row[2]: num_unverifiable_no_pub_key+=1
                total_entries+=1
                
        file.close()
        total_key_expired = num_goods_key_expired+num_bads_key_expired+num_unverifiable_key_expired
        total_no_pub_key = num_goods_no_pub_key+num_bads_no_pub_key+num_unverifiable_no_pub_key

    return {'total_entries': total_entries, 'num_goods':num_goods, 'num_bads':num_bads, 'num_unverifiables':num_unverifiable,
            'total_key_expired':total_key_expired, 'num_goods_key_expired':num_goods_key_expired, 
            'num_bads_key_expired':num_bads_key_expired, 'num_unverifiables_key_expired':num_unverifiable_key_expired,
            'total_no_pub_key':total_no_pub_key, 'num_goods_no_pub_key':num_goods_no_pub_key, 
            'num_bads_no_pub_key':num_bads_no_pub_key, 'num_unverifiables_no_pub_key':num_unverifiable_no_pub_key}, keys
            

def get_ratio(sub_val, total):
    """
    Quick helper function to format the counts into ratio

    sub_val: number of counts

    total: total number of counts

    returns: float ratio value formatted to 2 decimal points
    """
    ratio = "{:.2f}".format(float(sub_val) / total * 100 if total !=0 else float(0.00))

    return ratio


def sortby(x):
    """
    Sorts the table by date order
    """
    return int(x.split('_')[2].split('.')[0])

def compute_metrics(lib, date_range):
    """
    Formats the counted values, generate a table

    lib: library to process

    date_range: files published before date_range is counted
    """
    os.makedirs(f'{scratch_space}/metrics/{date_range}/', exist_ok=True)
    metrics_path = f'{scratch_space}/metrics/{date_range}/{lib}_{date_range}_metrics.csv'

    tables = os.listdir(f'../data/outputs/{lib}/tables/')
    tables.sort(key=sortby)
    print(tables)
    global_keys = []
    global_row = {}

    no_signs = get_metrics_no_signs(lib, date_range)

    with open(metrics_path, 'a', newline='') as metrics_file:
        csv_writer = csv.writer(metrics_file)
        for i, table in enumerate(tables):
            
            # Generate dictionary with entries from the table
            maven_dict = generate_maven_dict(lib, table, date_range)
            
            # Generate a result metrics for each tables in outputs directory
            new_row, global_keys = get_metrics(table, global_keys, maven_dict)
            # Update the global_row to write to the file
            if not global_row:
                # First table becomes the value itself to global_row
                global_row = new_row
            else:
                # Add values up to the global_row, which contains the total values from all tables
                for key in global_row.keys():
                    global_row[key] += new_row[key]
            del maven_dict
            print(new_row)

        ratio_goods = get_ratio(global_row['num_goods'], global_row['total_entries'])
        ratio_bads = get_ratio(global_row['num_bads'], global_row['total_entries'])
        ratio_unverifiables = get_ratio(global_row['num_unverifiables'], global_row['total_entries'])
        
        ratio_goods_key_expired = get_ratio(global_row['num_goods_key_expired'], global_row['total_key_expired'])
        ratio_bads_key_expired = get_ratio(global_row['num_bads_key_expired'], global_row['total_key_expired'])
        ratio_unverifiables_key_expired = get_ratio(global_row['num_unverifiables_key_expired'], global_row['total_key_expired'])
        
        ratio_goods_no_pub_key = get_ratio(global_row['num_goods_no_pub_key'], global_row['total_no_pub_key'])
        ratio_bads_no_pub_key = get_ratio(global_row['num_bads_key_expired'], global_row['total_no_pub_key'])
        ratio_unverifiables_no_pub_key = get_ratio(global_row['num_unverifiables_key_expired'], global_row['total_no_pub_key'])

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
        print(final_row)
        csv_writer.writerow(list(final_row.keys()))
        csv_writer.writerow(list(final_row.values()))
        metrics_file.close()    

    # df = pd.read_csv(metrics_path)
    # print(df)


if __name__ == '__main__':
    """
    After the run, there should be {lib}_{date_range}_metrics.csv in {scratch_space}/metrics/{date_range}/
    """ 
    # Generate metrics table up to given date
    compute_metrics(lib, date_range)




    