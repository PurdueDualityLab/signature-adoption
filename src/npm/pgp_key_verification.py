import requests
import subprocess

def verify_npm_package_pgp_signature(package_name, version):
    """
    Verify the PGP signature of an npm package using Keybase CLI.

    Args:
    - package_name (str): The name of the npm package.
    - version (str): The version of the npm package to check.

    Returns:
    - (str): The result of the PGP signature verification.
    """
    # Fetch the package's signature and integrity value
    url = f"https://registry.npmjs.org/{package_name}/{version}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    signature = data["dist"]["npm-signature"]
    integrity = data["dist"]["integrity"]
    
    # Save the signature to a temporary file
    with open("sig-to-check", "w") as f:
        f.write(signature)
    
    # Construct the verification command
    cmd = [
        "keybase", "pgp", "verify", "--signed-by", "npmregistry",
        "-d", "sig-to-check",
        "-m", f"{package_name}@{version}:{integrity}"
    ]
    
    # Execute the command and get the result
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return result.stdout

# Example usage:
package_name = "light-cycle"
version = "1.4.3"
verification_result = verify_npm_package_pgp_signature(package_name, version)
print(verification_result)

# https://web.archive.org/web/20230510052407/https://docs.npmjs.com/verifying-the-pgp-signature-for-a-package-from-the-npm-public-registry
