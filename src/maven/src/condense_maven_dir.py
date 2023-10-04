import os
import csv

# Second file to run
"""
Condense down the number of entries in {lib}.csv by putting associated files into one entry
"""

def process_buffer(curr_dir_buffer, csv_writer):
    """
    Processes the csvs in maven_dir by condensing down the number 
    of rows, file names with multiple extensions become one entry
    
    curr_dir_buffer: list containing associated extensions to a file

    csv_writer: the csv writer to write with.
    """
    dir = curr_dir_buffer[0][0]

    # Get a list of file names sorted by length
    file_names = []
    for file in curr_dir_buffer:
        file_names.append(file[2])
    file_names = sorted(file_names, key=len)

    unique_files = []

    while len(file_names) > 0:
        
        name = file_names[0]
        subset = [f for f in file_names if f.startswith(name)]
        file_names = [f for f in file_names if f not in subset]
        subset = [f[len(name):] for f in subset]
        subset = [f for f in subset if f is not '']

        unique_files.append((name, subset))
    
    for uf in unique_files:
        csv_writer.writerow([dir, uf[0], ",".join(uf[1])])


if __name__ == '__main__':
    """
    After the run of the program, there should be condensed_{dir_name}.csv
    file existing in local_condensed_file_path
    """

    # Run one by one with different jobs for parallel processing
    # [aws, com, dev, io, libs, net, org, software]
    lib = 'aws'

    local_log_file_path = f'../data/maven_dirs/{lib}.csv'
    local_condensed_file_path = f'../data/condensed/'

    # Create a directory to place the file
    os.makedirs(local_condensed_file_path, exist_ok=True)

    local_condensed_file_path += f'condensed_{lib}.csv'
    with open(local_log_file_path, 'r', newline='') as log_file:
        with open(local_condensed_file_path, 'a', newline='') as condensed_file:
            
            csv_writer = csv.writer(condensed_file)
            csv_reader = csv.reader(log_file)

            # Manually populate with first field
            curr_dir_buffer = []
            first = csv_reader.__next__()
            curr_dir_buffer.append(first)

            # Iterate through all lines in the file
            for row in csv_reader:
                
                # Check for empty directory
                if row[1] == 'EMPTY_DIR':
                    continue
                
                # Check if next file is in same dir
                if row[0] == curr_dir_buffer[0][0]:
                    curr_dir_buffer.append(row)
                
                # New dir
                else:
                    process_buffer(curr_dir_buffer=curr_dir_buffer,
                        csv_writer=csv_writer)
                    curr_dir_buffer = []
                    curr_dir_buffer.append(row)
            
            # Process the last directory
            process_buffer(curr_dir_buffer=curr_dir_buffer,
                        csv_writer=csv_writer)


