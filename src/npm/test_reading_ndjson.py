import json

def read_ndjson(file_path: str):
    with open(file_path, 'r') as f:
        for line in f:
            yield json.loads(line)

if __name__ == '__main__':
    i = 0
    for record in read_ndjson('./packages_npm.ndjson'):
        print(record["versions"])
        print((record['versions'][0]['signatures']))
        print(len(record['versions']))
        print("\nbreak\n\n")
        if(i >= 3):
            break
        i += 1
