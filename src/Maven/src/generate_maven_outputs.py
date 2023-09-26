import os
import csv
import argparse
import requests
import subprocess

# Fourth file to run
"""
Generate table containing verified signature result by {lib}
Run the jobs through generate_maven_output_jobs.py
"""

# path to store local downloads
scratch_space = f'../data/maven_files/'
os.makedirs(scratch_space, exist_ok=True)

def download_file(remote_file_path, local_file_path):
    """
    Locally download signature file and associate data file to local_file_path

    remote_file_path: path targetting file from Maven Central

    local_file_path: path to download files to

    returns: True or False, whether files exist and downloaded successfully or not
    """
    
    response = requests.get(remote_file_path)
    if response:
        # Temporily save remote files to scratch space
        with open(scratch_space+local_file_path, "wb") as local_file:
            local_file.write(response.content)
        local_file.close()
        return True
    return False

def verify_signature(local_sign_file, local_data_file):
    """
    Verify the signature

    local_sign_file: signature file

    local_data_file: associate data file

    returns: readable verification result
    """
    try:
        output = subprocess.check_output(["gpg", "--keyserver-option", "auto-key-retrieve", "--keyserver", "keyserver.ubuntu.com",
                                            "--verify", local_sign_file, local_data_file], stderr=subprocess.STDOUT)
        return output.decode("utf-8")
    except subprocess.CalledProcessError as e:
        # print(f"Error verifying signature: {e}")
        return e.output
    

# write_from: data file & sign file, write_to: root_pkg dir in scratch space
def generate_outputs(signs_buffer, valid_output_logger):
    """
    Generating output table by each lib

    signs_buffer: signature file

    local_data_file: associate data file

    returns: readable verification result
    """
    local_sign_path = signs_buffer[1]
    local_data_path = signs_buffer[2]
    remote_sign_path = signs_buffer[0] + local_sign_path
    remote_data_path = signs_buffer[0] + local_data_path

    sign_result = download_file(remote_sign_path, local_sign_path)
    data_result = download_file(remote_data_path, local_data_path)
    
    # Both files are valid
    if sign_result and data_result:
        
        output = verify_signature(scratch_space+local_sign_path, scratch_space+local_data_path)
        if os.path.exists(scratch_space+local_sign_path):
            os.remove(scratch_space+local_sign_path)
        if os.path.exists(scratch_space+local_data_path):
            os.remove(scratch_space+local_data_path)
        valid_output_logger.writerow([signs_buffer[0], local_sign_path, output])


if __name__ == "__main__":
    """
    After the run, there should be outputs_{lib}_{start_ind}.csv in local_outputs_tables_path
    """ 

    # Parse the argument from jobs
    parser = argparse.ArgumentParser()
    parser.add_argument('inputs', nargs='+')
    args = parser.parse_args()
    # Assuming program is ran with 2 integer arguments 
    start_ind = int(args.inputs[0])
    end_ind = int(args.inputs[1])

    # 1. Run one by one with different jobs for parallel processing
    # [aws, com, dev, io, libs, net, org, software]
    lib = 'aws'

    local_signs_path = f'../data/signs/signs_{lib}.csv'
    local_outputs_tables_path = f'../data/outputs/{lib}/tables/'
    
    # Create a directory to place the file
    os.makedirs(local_outputs_tables_path, exist_ok=True)
    
    local_outputs_tables_path += f'outputs_{lib}_{start_ind}.csv'
    with open(local_signs_path, 'r', newline='') as signs_file:
        with open(f'{local_outputs_tables_path}outputs_{lib}_{start_ind}.csv', 'a', newline='') as outputs_file:
        
            csv_reader = csv.reader(signs_file)
            valid_output_writer = csv.writer(outputs_file)
            
            for i, row in enumerate(csv_reader):
                if start_ind <= i and i <= end_ind:
                    generate_outputs(row, valid_output_writer)
        
        outputs_file.close()
    signs_file.close()