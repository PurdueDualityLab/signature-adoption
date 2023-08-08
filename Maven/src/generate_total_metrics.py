import os
import csv
import pandas as pd
from datetime import datetime

# Last file to run
"""
1. Combine the metrics table by library into one, generates total count
2. Combine the metrics tables by date into one, extracting out the total counts into one
"""

scratch_space = f'../data/outputs/'

def get_ratio(sub_val, total):
    """
    Quick helper function to format the counts into ratio

    sub_val: number of counts

    total: total number of counts

    returns: float ratio value formatted to 2 decimal points
    """
    ratio = "{:.2f}".format(float(sub_val) / total * 100 if total !=0 else float(0.00))

    return ratio


def compute_metrics(libs, date_range, final_metrics_path):
    """
    Target each namespace tables, combine into one big table

    libs: list of libraries to process

    date_range: files published before date_range is counted

    final_metrics_path: path where tables will be combined to
    """
    flag = 1
    with open(final_metrics_path, 'a', newline='') as metrics_file:
        csv_writer = csv.writer(metrics_file)
        # Target each individual metrics tables
        for lib in libs:
            files = [file for file in os.listdir(f'{scratch_space}/{lib}/metrics/{date_range}') if file.endswith('csv')]
            # Open each metrics table
            print(f'Processing {lib}..')
            for file in files:
                with open(f'{scratch_space}{lib}/metrics/{date_range}/{file}', 'r', newline='') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    csv_list = list(csv_reader)
                    # Insert namespace for each metrics table
                    if flag:
                        keys = csv_list[0]
                        # Generate column names
                        keys.insert(0, 'namespace')
                        csv_writer.writerow(keys)
                        flag = 0
                    comp_values = []
                    # Entries in 'lib'_metrics.csv
                    for i, row in enumerate(csv_list):
                        
                        # Write the odd indexes(actual numbers)
                        if i % 2 == 1:
                            if comp_values == []:
                                comp_values = row
                            else:
                                for i in range(len(comp_values)):
                                    comp_values[i] = float(comp_values[i]) + float(row[i])
                    
                    lib_name = file.split('_')[0]
                    comp_values.insert(0, lib_name)
                    csv_writer.writerow(comp_values)


def include_total(final_metrics_path):
    """
    Include a row for total count

    final_metrics_path: path where tables will be combined to
    """
    df = pd.read_csv(final_metrics_path)

    total_row = df.sum(numeric_only=True).to_dict()
    # print(total_row)
    # total_row['namespace'] = 'Total'
    namespace_col = pd.Series({'namespace': 'Total'})

    total_row['ratio_goods'] = get_ratio(total_row['num_goods'], total_row['total_entries'])
    total_row['ratio_bads'] = get_ratio(total_row['num_bads'], total_row['total_entries'])
    total_row['ratio_unverifiables'] = get_ratio(total_row['num_unverifiables'], total_row['total_entries'])

    total_row['ratio_goods_key_expired'] = get_ratio(total_row['num_goods_key_expired'], total_row['total_key_expired'])
    total_row['ratio_bads_key_expired'] = get_ratio(total_row['num_bads_key_expired'], total_row['total_key_expired'])
    total_row['ratio_unverifiables_key_expired'] = get_ratio(total_row['num_unverifiables_key_expired'], total_row['total_key_expired'])

    total_row['ratio_goods_no_pub_key'] = get_ratio(total_row['num_goods_no_pub_key'], total_row['total_no_pub_key'])
    total_row['ratio_bads_no_pub_key'] = get_ratio(total_row['num_bads_no_pub_key'], total_row['total_no_pub_key'])
    total_row['ratio_unverifiables_no_pub_key'] = get_ratio(total_row['num_unverifiables_no_pub_key'], total_row['total_no_pub_key'])

    total_row = pd.concat([namespace_col, pd.Series(total_row)])
    # print(total_row)


    df = df.sort_values(by='namespace', ignore_index=True)
    df = pd.concat([total_row.to_frame().T, df], ignore_index=True)
    # print(df)
    df.to_csv(final_metrics_path)


def sortby(x):
    """
    Sorts the table by date order
    """
    return datetime.strptime(x.split('_')[0], '%Y-%m-%d')


def get_totals_from_date(date_from_to, path):
    """
    Generate a group of total counts from metrics table by date into one

    path: path to generate a table to
    """

    metrics_tables = [file for file in os.listdir(path) if file.endswith('.csv')]
    metrics_tables.sort(key=sortby)

    columns = []
    total_entries = []
    is_first = True
    for i, table in enumerate(metrics_tables, 1):

        with open(f'{path}{table}', 'r', newline='') as metrics_file:
            
            csv_reader = csv.reader(metrics_file)
            csv_list = list(csv_reader)
            if is_first:
                # Change namespace to date
                csv_list[0][1] = 'date'
                columns = csv_list[0]
                is_first = False

            csv_list[1][0] = i
            csv_list[1][1] = table.split('_')[0]
            total_entries.append(csv_list[1])
        metrics_file.close()

    
    df = pd.DataFrame(total_entries, columns=columns)
    df.to_csv(f'{path}/{date_from_to}/{date_from_to}_metrics.csv', index=False)


if __name__ == '__main__':
    """
    After compute_metrics() and include_total(), there should be {date_range}_metrics.csv 
    in final_metrics_path.
    After get_totals_from_date(), there should be {date_from_to}_metrics.csv in {from_to_path}/{date_from_to}
    """ 
    date_range = '2015-08-11'
    final_metrics_path = f'../data/metrics_tables/'
    os.makedirs(f'{final_metrics_path}', exist_ok=True)
    final_metrics_path += f'{date_range}_metrics.csv'
    libs = ['aws', 'com', 'dev', 'io', 'libs', 'net', 'org', 'software']
    compute_metrics(libs, date_range, final_metrics_path)
    include_total(final_metrics_path)

    from_to_path = f'../data/metrics_tables/'
    date_from_to = '2015-08-11_2023-08_04'
    os.makedirs(f'{from_to_path}/{date_from_to}', exist_ok=True)
    get_totals_from_date(date_from_to, from_to_path)