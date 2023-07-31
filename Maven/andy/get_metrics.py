import os
import csv
import pandas as pd
import numpy as np
from automate_signatures import append_row
import warnings
from pathlib import Path


warnings.filterwarnings("ignore")


def concat_from_valid(lib_name):
    # maven_csv_path = f'/scratch/bell/ko112/maven_csvs/valid_csvs/{lib_name}/'
    valid_csv = f'/scratch/bell/ko112/maven_csvs/valid_csvs/maven_{lib_name}.csv'
    
    concat_csv = f'/scratch/bell/ko112/maven_csvs/concat_csvs/maven_{lib_name}.csv'
    # concat_csv2 = f'/scratch/bell/ko112/maven_csvs/concat_csvs/maven_{lib_name}2.csv'

    
    columns=['package_name', 'version', 'file_name', 'url', 'raw_output', 'signature_date', 'signature_key', 'request_key',
              'signature_validity', 'signature_trusted', 'signature_indication', 'primary_key_fingerprint']
    extra_cols = [col for col in range(30)]
    columns += extra_cols
    valid_df = (
        pd.read_csv(valid_csv, names=columns, engine='python', encoding='utf8', header=None, index_col=0, skiprows=1).reset_index(level=0)
    )
    # for i in range(valid_df.shape[1]-1):
    #     valid_df.iloc[:, i] = valid_df.iloc[:, i+1]
    concat_df = pd.read_csv(concat_csv)
    print(valid_df.head())
    print(concat_df.head())
    

    combined_data = pd.DataFrame()
    combined_data = pd.concat([valid_df, concat_df], ignore_index=True)
    for i in range(combined_data.shape[1]-1):
        combined_data.iloc[:, i] = combined_data.iloc[:, i+1]
    combined_data = combined_data.drop_duplicates()
    print(combined_data.shape)
    print(combined_data.head())
    print(combined_data.tail())
    combined_data.to_csv(concat_csv, index=False)
    

def concat_csvs(lib_name):
    # maven_csv_path = f'/scratch/bell/ko112/maven_csvs/valid_csvs/{lib_name}/'
    maven_csv_path = f'/scratch/bell/ko112/maven_csvs/valid_csvs/{lib_name}/'
    
    # concat_csv_path = f'/scratch/bell/ko112/maven_csvs/concat_csvs/concat_maven_{lib_name}.csv'  # Replace with the desired output file path
    concat_csv_path = f'/scratch/bell/ko112/maven_csvs/concat_csvs/maven_{lib_name}.csv'  # Replace with the desired output file path

    # Get a list of all CSV files in the directory
    # csvs = [file for file in os.listdir(maven_csv_path)]
    
    columns=['package_name', 'version', 'file_name', 'url', 'raw_output', 'signature_date', 'signature_key', 'request_key',
              'signature_validity', 'signature_trusted', 'signature_indication', 'primary_key_fingerprint']
    extra_cols = [col for col in range(30)]
    columns += extra_cols
    maven_csvs = Path(maven_csv_path)
    dfs = (
        pd.read_csv(p, names=columns, engine='python', encoding='utf8', header=None, index_col=0, skiprows=1).reset_index(level=0) for p in maven_csvs.glob('*.csv')
    )
    
    # Create an empty DataFrame to store the concatenated data
    combined_data = pd.DataFrame()
    # Concatenate all CSV files
    combined_data = pd.concat(dfs, ignore_index=True)
    # for i in range(combined_data.shape[1]-1):
    #     combined_data.iloc[:, i] = combined_data.iloc[:, i+1]
    # combined_data = combined_data.drop_duplicates()
    combined_data.to_csv(concat_csv_path, index=False)
    print(combined_data.head())
    print(combined_data.tail())

def get_lines(csv_path):
    len = 0
    with open(csv_path, 'r') as file:
        df = csv.reader(file)
        for row in df:
            if '/' in row[1]:
                len+=1
    return len

def get_invalids(lib_name):
    invalids_df = pd.read_csv(f'/scratch/bell/ko112/maven_csvs/invalid_csvs/maven_invalids.csv')
    # invalids_df = invalids_df.drop_duplicates()
    count = 0
    no_data = 0
    no_signs = 0
    neither = 0
    for i in range(len(invalids_df)):
        if f'/maven2/{lib_name}/' in invalids_df.loc[i, 'url']:
            count+=1
            if 'Empty directory' in invalids_df.loc[i, 'reason']: neither+=1
            elif 'Unable to download, bad url' in invalids_df.loc[i, 'reason']: no_data+=1
            elif 'No signature file found' in invalids_df.loc[i, 'reason']: no_signs+=1
    return count, no_data, no_signs, neither  

def get_metrics_df(lib_name):
    
    csv_path = f'/scratch/bell/ko112/maven_csvs/concat_csvs/maven_{lib_name}.csv'
    
    num_goods = 0
    num_bads = 0
    num_unverifiable = 0
    num_keys_used = 0
    good_key_expired = 0
    bad_key_expired = 0
    bad_no_public_key = 0
    xver_no_public_key = 0
    # badlist = []
    elselist = []
    # df = pd.read_csv(csv_path).drop_duplicates()
    
    invalids, xver_no_data, xver_no_signs, xver_neither = get_invalids(lib_name)
    
    df = pd.read_csv(csv_path)
    total_size = df.shape[0] + invalids
    current_key = ''
    for ind, row in df.iterrows():
        if type(row['raw_output']) == str and type(row['signature_key']) == str:
            if 'key ID' in row['raw_output'] and current_key != row['signature_key']:
                    num_keys_used+=1
                    current_key = row['signature_key']
                    # print(f'Current key: {current_key}')
            if 'Good' in row['raw_output']: 
                num_goods+=1
                if 'expired' in row['raw_output']:
                    good_key_expired+=1
            elif 'BAD' in row['raw_output'] or 'Bad' in row['raw_output']: 
                num_bads+=1
                if 'No public key' in row['raw_output']: bad_no_public_key+=1
                if 'expired' in row['raw_output']: bad_key_expired+=1
            # elif 'imported' in row[9]:
            #     if 'Good' in row[9]: num_goods+=1
            #     elif 'Bad' in row[9]: 
            #         badlist.append(row[4])
            #         num_bads+=1
            else:
                xver_no_public_key+=1
                num_unverifiable+=1
                    
    num_unverifiable += invalids
    if num_unverifiable != xver_no_data + xver_no_signs + xver_neither + xver_no_public_key:
        print(elselist)
        return
    ratio_goods = round(num_goods/total_size, 4) * 100
    ratio_bads = round((num_bads)/total_size, 4) * 100
    ratio_unverifiable = round((num_unverifiable)/total_size, 4) * 100
    totals_match = total_size == num_goods+num_bads+num_unverifiable
    xver_match = num_unverifiable == xver_no_public_key+xver_no_data+xver_no_signs+xver_neither
    new_row = {'library': [lib_name], 'total_size': [total_size], 'num_goods': [num_goods], 'num_bads':[num_bads], 'num_unverifiable': [num_unverifiable], 
            'totals_match': [totals_match], 'ratio_goods': [ratio_goods], 'ratio_bads': [ratio_bads], 
            'ratio_unverifiable': [ratio_unverifiable], 'num_keys_used': [num_keys_used], 'good_key_expired': [good_key_expired], 'bad_key_expired': [bad_key_expired], 'bad_no_public_key': [bad_no_public_key], 'xver_no_public_key': [xver_no_public_key], 
            'xver_no_data' :[xver_no_data], 'xver_no_signs': [xver_no_signs], 'xver_no data_and_sign': [xver_neither], 'xver_match': [xver_match]}
    print(new_row)
    new_row = pd.DataFrame(new_row)
    csv_path = '/scratch/bell/ko112/maven_csvs/df_maven_metrics.csv'
    if not os.path.exists(csv_path):
        new_row.to_csv(csv_path, index=False)
    else:
        metrics_csv = pd.read_csv(csv_path)
        concat_csv = pd.concat([metrics_csv, new_row], ignore_index=True)
        concat_csv.to_csv(csv_path, index=False)

# Targeting dir in 'com/' modify later
def get_metrics(lib_name):

    csv_path = f'/scratch/bell/ko112/maven_csvs/valid_csvs/maven_{lib_name}.csv'
    
    num_goods = 0
    num_bads = 0
    num_unverifiable = 0
    num_keys_used = 0
    good_key_expired = 0
    bad_key_expired = 0
    bad_no_public_key = 0
    xver_no_public_key = 0
    # badlist = []
    elselist = []
    # df = pd.read_csv(csv_path).drop_duplicates()
    
    invalids, xver_no_data, xver_no_signs, xver_neither = get_invalids(lib_name)
    total_size = get_lines(csv_path) + invalids
    with open(csv_path, 'r') as file:
        df = csv.reader(file)
        current_key = ''
        for row in df:
            if '/' in row[1]:
                if 'key ID' in row[7] and current_key != row[7]:
                        num_keys_used+=1
                        current_key = row[7]
                        # print(f'Current kc:qey: {current_key}')
                if 'Good' in row[5]: 
                    num_goods+=1
                    if 'expired' in row[5]:
                        good_key_expired+=1
                elif 'BAD' in row[5] or 'Bad' in row[5]: 
                    num_bads+=1
                    if 'No public key' in row[5]: bad_no_public_key+=1
                    if 'expired' in row[5]: bad_key_expired+=1
                # elif 'imported' in row[9]:
                #     if 'Good' in row[9]: num_goods+=1
                #     elif 'Bad' in row[9]: 
                #         badlist.append(row[4])
                #         num_bads+=1
                else:
                    xver_no_public_key+=1
                    num_unverifiable+=1
                    
        num_unverifiable += invalids
        if num_unverifiable != xver_no_data + xver_no_signs + xver_neither + xver_no_public_key:
            # print(elselist)
            return
        ratio_goods = round(num_goods/total_size, 4) * 100
        ratio_bads = round((num_bads)/total_size, 4) * 100
        ratio_unverifiable = round((num_unverifiable)/total_size, 4) * 100
        totals_match = total_size == num_goods+num_bads+num_unverifiable
        new_row = {'library': [lib_name], 'total_size': [total_size], 'num_goods': [num_goods], 'num_bads':[num_bads], 'num_unverifiable': [num_unverifiable], 
                'totals_match': [totals_match], 'ratio_goods': [ratio_goods], 'ratio_bads': [ratio_bads], 
                'ratio_unverifiable': [ratio_unverifiable], 'num_keys_used': [num_keys_used], 'good_key_expired': [good_key_expired], 'bad_key_expired': [bad_key_expired], 'bad_no_public_key': [bad_no_public_key], 'xver_no_public_key': [xver_no_public_key], 
                'xver_no_data' :[xver_no_data], 'xver_no_signs': [xver_no_signs], 'xver_no data_and_sign': [xver_neither]}
        
        new_row = pd.DataFrame(new_row)
        print(new_row.head())
        csv_path = '/scratch/bell/ko112/maven_csvs/maven_metrics.csv'
        if not os.path.exists(csv_path):
            new_row.to_csv(csv_path, index=False)
        else:
            metrics_csv = pd.read_csv(csv_path)
            concat_csv = pd.concat([metrics_csv, new_row], ignore_index=True)
            concat_csv.to_csv(csv_path, index=False)


# /com/jslsolucoes
# concat_from_valid('software')
# concatenate: dev/ io/ net/ software/ com/
# done : dev/ io/ net/ software/
# dont need concatenate: org/
# df_metrics done: net/ dev/ software
# df_metrics curr: io/
# df_metrics need: io/ org/ com/



# get_metrics_df('dev')
# concat_csvs('net')
# concat_from_valid('net')
# get_metrics_df('net')
# get_metrics_df('dev')

# concat_csvs('io')
# concat_from_valid('io')
# get_metrics_df('io')

# concat_csvs('net')
# concat_from_valid('net')
# get_metrics_df('net')
# concat_csvs('software')
# concat_from_valid('software')
# get_metrics_df('software')

# concat_csvs('com')
# concat_from_valid('com')
# get_metrics_df('com')



# path = '/scratch/bell/ko112/maven_csvs/concat_csvs/maven_net.csv'
# csv_dirs = [file for file in os.listdir(path) if file.endswith('.csv')]
# for file in csv_dirs:
#     get_metrics(file[10:-4])
# path = '/scratch/bell/ko112/maven_csvs/concat_csvs/maven_com.csv'
# concat_csvs('com')
# df = pd.read_csv(path)
# print(df.head())
# print(df.tail())


# read form valid_csvs/
# path = '/scratch/bell/ko112/maven_csvs/valid_csvs/maven_it.csv'
# len = 0
# with open(path, 'r') as file:
#     df = csv.reader(file)
#     for row in df:
#         len+=1
#         print(row)
#         if len ==5:
#             break



# get_metrics_df('io')
# get_metrics_df('com')



# concat_from_valid('software')


# Concatenate the csvs in concat_csvs/ and generate df_maven_metrics.csv
# csvpath = f'/scratch/bell/ko112/maven_csvs/valid_csvs/maven_it.csv'
# csvpath = f'/scratch/bell/ko112/maven_csvs/concat_csvs/maven_io.csv'
# df = pd.read_csv(csvpath)
# print(df.iloc[0, 4])
# print(df.shape)
# print(df.head())
# print(df.tail())

# csv_dirs = [file for file in os.listdir(csvpath) if file.endswith('.csv')]
# for csv_dir in csv_dirs:
#     print(csv_dir)
    # concat_csvs(csv_dir)
    # df = pd.read_csv(f'{csvpath}maven_{csv_dir}.csv')
# get_metrics_df(csv_dir[6:-4])

# df = pd.read_csv(f'/scratch/bell/ko112/maven_csvs/df_maven_metrics.csv')
# print(df.head())


# Re-run them once concatenate is done to generate maven_metrics.csv
# dirpath = f'/scratch/bell/ko112/maven_csvs/valid_csvs/'
# csv_dirs = [file for file in os.listdir(dirpath) if file.endswith('.csv')]
# for csv_dir in csv_dirs:
#     # concat_csvs(csv_dir)
#     lib_name = csv_dir[6:-4]
#     print(lib_name)
#     get_metrics(lib_name)
# df = pd.read_csv(f'/scratch/bell/ko112/maven_csvs/maven_metrics.csv')
# print(df.head())
