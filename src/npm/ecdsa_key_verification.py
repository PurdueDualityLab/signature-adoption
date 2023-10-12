import requests
import base64
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

def fetch_packument(package_name):
    url = f"https://registry.npmjs.org/{package_name}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def fetch_public_keys():
    url = "https://registry.npmjs.org/-/npm/v1/keys"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["keys"]

def verify_signature(package_name, version):
    # Fetch the packument
    packument = fetch_packument(package_name)
    version_data = packument["versions"][version]
    signature_data = version_data["dist"]["signatures"][0]
    
    # Fetch the public keys
    public_keys = fetch_public_keys()
    
    # Find the correct public key for the signature
    public_key_data = next((key for key in public_keys if key["keyid"] == signature_data["keyid"]), None)
    if not public_key_data:
        raise ValueError("Public key not found for signature.")
    
    # Extract the public key
    public_key_bytes = base64.b64decode(public_key_data["key"])
    public_key = serialization.load_der_public_key(public_key_bytes, backend=default_backend())
    
    # Prepare the data to be verified
    verification_data = f"{package_name}@{version}:{version_data['dist']['integrity']}".encode('utf-8')
    
    # Verify the signature
    signature = base64.b64decode(signature_data["sig"])
    try:
        public_key.verify(signature, verification_data, ec.ECDSA(hashes.SHA256()))
        return True
    except:
        return False

if __name__ == "__main__":
    package_name = "react"
    version = "18.2.0"
    is_valid = verify_signature(package_name, version)
    print(f"Signature is {'valid' if is_valid else 'invalid'} for {package_name}@{version}")

