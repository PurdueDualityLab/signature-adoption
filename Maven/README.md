# Maven
Scripts used to collect packages from Maven Central repository.

## Steps to Run the Scripts

1. **Clone the Repository:**
Clone the main repository to your local machine using the following command:
git clone https://github.com/PurdueDualityLab/signature-adoption.git

2. **Navigate to Directory:**
Change your working directory to ~/signature-adoption/Maven/src
cd ~/signature-adoption/Maven/src

3. **Install Dependencies:**
Create and activate anaconda environment with environment.yml
conda env create -f environment.yml
conda activate maven

4. **Run files in order:**
    1. generate_maven_dir.py
    2. condense_maven_dir.py
    3. generate_maven_signs.py
    4. generate_maven_outputs.py, generate_maven_outputs_jobs.py
    5. generate_metrics_by_date.py, generate_maven_metrics_libs_by_date.py
    6. generate_total_metrics.py
- Refer to comments on each files before the execution. We used Bell computing server to execute the programs, and up to 5 days were taken to run step iv.

