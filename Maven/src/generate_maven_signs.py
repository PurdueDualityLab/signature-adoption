import csv
import os

# Third file to run
"""
From the entries in condensed_path, indicate which entries have signature
file, record in either local_signs_path or local_no_signs_path
"""

def generate_valid_signatures(dir_buffer, signs_logger):
    """
    Record entries that have a signature file

    dir_buffer: each row entry from the condensed file

    signs_logger: logger used to write entry in signs_file_path
    """
        
    file_path = dir_buffer[0]
    data_file = dir_buffer[1]
    sign_file = dir_buffer[1] + '.asc'
    signs_logger.writerow([file_path, sign_file, data_file])


def generate_no_signatures(dir_buffer, no_signs_logger):
    """
    Record entries that doesn't have a signature file

    dir_buffer: each row entry from the condensed file

    no_signs_logger: logger used to write entry in no_signs_file_path
    """ 

    file_path = dir_buffer[0]
    file_name = dir_buffer[1]
    no_signs_logger.writerow([file_path, file_name])

if __name__ == "__main__":
    """
    After the run, there should be signs_{lib}.csv in local_signs_path
    and no_signs_{lib}.csv in local_no_signs_path
    """ 

    # Run one by one with different jobs for parallel processing
    # [aws, com, dev, io, libs, net, org, software]
    lib = 'aws'

    local_signs_path = f'../data/signs/'
    local_no_signs_path = f'../data/no_signs/'
    local_condensed_path = f'../data/condensed/condensed_{lib}.csv'

    # Create a directory to place the file
    os.makedirs(local_signs_path, exist_ok=True)
    os.makedirs(local_no_signs_path, exist_ok=True)
    
    local_signs_path += f'signs_{lib}.csv'
    local_no_signs_path += f'no_signs_{lib}.csv'
    with open(local_condensed_path, 'r', newline='') as condensed_file:
        with open(local_signs_path, 'a', newline='') as signs_file:
            with open(local_no_signs_path, 'a', newline='') as no_signs_file:
            
                csv_reader = csv.reader(condensed_file)
                valid_signs_writer = csv.writer(signs_file)
                no_signs_writer = csv.writer(no_signs_file)
                
                for row in csv_reader:
                    
                    if row[2]:
                        # Signature file found
                        if '.asc' in row[2]:
                            generate_valid_signatures(row, valid_signs_writer)
                        # Signature file not found
                        else:
                            generate_no_signatures(row, no_signs_writer)
                    # Signature file not found
                    else:
                        generate_no_signatures(row, no_signs_writer)
                    
            no_signs_file.close()
        signs_file.close()
    condensed_file.close()
