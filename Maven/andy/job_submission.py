import subprocess as sb
from automate_signatures import divide_dirs


def write_job(job_id, list_dirs):
    job_script = f"""#!/bin/bash
    #SBATCH --account=davisjam
    #SBATCH --nodes=1
    #SBATCH --time=96:00:00
    #SBATCH --job-name=job_{job_id}.sub
    #SBATCH --output=job_{job_id}.out
    #SBATCH --mail-type=begin
    #SBATCH --mail-type=end
    #SBATCH --mail-user=ko112@purdue.edu
    #SBATCH --export=all
    

    module load anaconda
    conda activate sample_env

    cd /home/ko112
    python automate_signatures.py {' '.join(list_dirs)}
    """

    with open(f'job_{job_id}.sub', 'w') as file:
        file.write(job_script)

def run_job(job_id):
    
    command = ['sbatch', f'job_{job_id}.sub']
    sb.run(command, text=True, capture_output=True)

    # output_log = 'output.log'
    # with open(f'job_{job_id}.out', 'r') as job_output:
    #     with open(output_log, "a") as log_file:
    #         log_file.write(f"{job_output.read()}")
    # sb.run(['rm', f'job_{job_id}.out', f'job_{job_id}.sub'])

    # pattern = r'slurm-\d+\.out'
    # files = os.listdir()
    # for file in files:
    #     if re.match(pattern.file):
    #         os.remove(file)

# divide the functionality by different batches, generate scripts to send as multiple jobs
class job_submission:
    def __init__(self):
        self.base_repo_url = 'https://repo1.maven.org/maven2/'
        self.batch_size = 100
        self.lists_dirs = divide_dirs(self.base_repo_url, self.batch_size)
        for job_id, list_dirs in enumerate(self.lists_dirs):
            write_job(job_id, list_dirs)
            run_job(job_id)


if __name__ == '__main__':
    job_submit = job_submission()

