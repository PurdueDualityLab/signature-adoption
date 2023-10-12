import json
import sys
from ecdsa_key_verification import verify_signature

# Set up logging
import logging
logging.basicConfig(level=logging.INFO)

MIN_VERSION_COUNT = 2
def has_min_version_count(npm_ndjson: dict):
    versions_len = len(npm_ndjson['versions'])
    if(versions_len < MIN_VERSION_COUNT):
        return False
    return True

MIN_DOWNLOADS_COUNT = 5
def has_min_downloads(npm_ndjson: dict):
    num_downloads = npm_ndjson['downloads']
    if(num_downloads is None or num_downloads < MIN_DOWNLOADS_COUNT):
        return False
    return True

def read_ndjson(file_path: str):
    with open(file_path, 'r') as f:
        for line in f:
            yield json.loads(line)

import requests

def has_signature(package_name, version):
    # Fetch the package's metadata from the npm registry
    url = f"https://registry.npmjs.org/{package_name}"
    response = requests.get(url)
    data = response.json()

    # Navigate to the specific version and check for the signatures field
    version_data = data.get("versions", {}).get(version, {})
    return "signatures" in version_data.get("dist", {})

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Give file path to the ndjson input file as a command line argument.")
        exit()

    ndjson_file_path = sys.argv[1]
    logging.info(f"ndjson_file_path == {ndjson_file_path}\n")
        
    # Iterate over each ndjson object
    # Find how many packages have good signature, bad signature, or no signature
    num_good_sigs = 0
    num_bad_sigs = 0
    num_no_sigs = 0
    with open('npm_output.ndjson', 'w') as outfile:
        for record in read_ndjson(ndjson_file_path):
            package_name = record['name']
            logging.info(f"Now analysing {package_name}")

            # Disregard packages that do not meet our criteria
            if(not has_min_downloads(record) or not has_min_version_count(record)):
                logging.info(f"{package_name} is being skipped.")
                continue

            # Verify signature for each version
            versions = record['versions']
            for index, version_info in enumerate(versions):
                version_number = version_info['number']

                # Check if there is no signature
                try:
                    if(not has_signature(package_name, version_number)):
                        logging.info(f"{package_name} version {version_number} does not have a signature.")

                        # Keep track of this in the ndjson record
                        record['versions'][index]['signature_status'] = "no signature"
                        num_no_sigs += 1
                        continue
                except:
                    logging.info(f"{package_name} version {version_number} error in checking if it has a signature.")
                    record['versions'][index]['signature_status'] = "could not find signature"
                    continue

                try: 
                    is_verified = verify_signature(package_name, version_number)
                    # TODO: Attempt to verify with PGP key as well.

                    if is_verified:
                        logging.info(f"{package_name} version {version_number} has a valid registry signature.")
                        num_good_sigs += 1
                    else:
                        logging.info(f"!{package_name} version {version_number} does has an invalid registry signature...!")
                        num_bad_sigs += 1
                except:
                    logging.info(f"{package_name} version {version_number} error in verifying signature.")
                    record['versions'][index]['signature_status'] = "could not verify signature"
                    continue

                # Add signature_status to the ndjson under the current version
                record['versions'][index]['signature_status'] = is_verified

            # Write updated record to output file
            outfile.write(json.dumps(record) + '\n')


    logging.info(f"Packages with good signatures: {num_good_sigs}\nPackages with bad signatures: {num_bad_sigs}\nPackages with no signatures: {num_no_sigs}")
    logging.info(f"Program complete!")

