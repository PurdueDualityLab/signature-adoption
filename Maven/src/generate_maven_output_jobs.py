import os
import csv
import subprocess

# Assigned number of jobs for each
# aws 1, com 30, dev 3, io 15, libs 7, net 2, software 3, org 30
lib = 'aws'
num_jobs = 1

# Replace the account if running through something like Bell
job_account = ''

local_signs_path = f'../data/signs/signs_{lib}.csv'
local_outputs_jobs_path = f'../data/outputs/{lib}/jobs/'
local_outputs_tables_path = f'../data/outputs/{lib}/tables/'

os.makedirs(local_outputs_jobs_path, exist_ok=True)
os.makedirs(local_outputs_tables_path, exist_ok=True)

def get_line_num(csv_path):
    """
    returns: the total number of lines in csv_path
    """
    line_counter = 0
    
    with open(csv_path, 'r', newline='') as file:
        
        for i, row in enumerate(file):
            line_counter=i
    
    file.close()

    return line_counter+1

def get_lines_to_process(job_id, signs_path):
    """
    returns: two indexes pointing start/stop of 
    """
    line_num = get_line_num(signs_path)
    
            
    start_ind = int(line_num / num_jobs) * job_id
    end_ind = int(line_num / num_jobs) * (job_id+1)

    # last job to send
    if job_id+1 == num_jobs:
        # Total length of file + 1
        end_ind = line_num+1

    return start_ind, end_ind


def write_job(lib, job_id, start_ind, end_ind):
    """
    Writes the job script to send over Bell computing server
    """
    job_script = f"""#!/bin/bash
#SBATCH --account={job_account}
#SBATCH --nodes=1
#SBATCH --time=240:00:00
#SBATCH --job-name=outputs_{lib}_{job_id}.sub
#SBATCH --output={local_outputs_jobs_path}outputs_{lib}_{job_id}.out
#SBATCH --mem-per-cpu=8G


python generate_maven_outputs.py {start_ind} {end_ind}
    """

    file_path = f'{local_outputs_jobs_path}outputs_{lib}_{job_id}'
    with open(f'{file_path}.sub', 'w') as file:
        file.write(job_script)

def run_job(lib, job_id):
    """
    Runs the job script over Bell computing server
    """

    file_path = f'{local_outputs_jobs_path}outputs_{lib}_{job_id}.sub'
    command = ['sbatch', file_path]
    subprocess.run(command)

print(f'{lib}: {get_line_num(local_signs_path)}')
for job_id in range(num_jobs):
    start_ind, end_ind = get_lines_to_process(job_id, local_signs_path)
    write_job(lib, job_id, start_ind, end_ind)
    run_job(lib, job_id)