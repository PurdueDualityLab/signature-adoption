import csv


local_log_file_path = '/home/tschorle/Maven/file_structure.csv'
# local_log_file_path = '/home/tschorle/Maven/testing.csv'
local_condensed_file_path = '/home/tschorle/Maven/file_condensed.csv'

num_empty_dir = 0

start = 0
stop = 100


def process_buffer(curr_dir_buffer, csv_writer):
    # print(f'{curr_dir_buffer[0][0]} has {len(curr_dir_buffer)} files.')

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

