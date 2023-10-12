import json

filename = "packages_npm.ndjson"

with open(filename, 'r') as file:
    name_to_search = '@primer/components'
    for idx, line in enumerate(file, start=1):
        obj = json.loads(line)
        if obj['name'] == name_to_search:
            result = f"Found '{name_to_search}' on line {idx}"
            break
    else:
        result = f"'{name_to_search}' not found in the file."
    print(f"Line of {name_to_search} is {result}.")

with open(filename, 'r') as file:
    line_count = sum(1 for _ in file)
    print(f"total lines in file: {line_count}.")

