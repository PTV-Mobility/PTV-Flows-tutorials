import subprocess
import sys
import re
import os
import shutil
from zipfile import ZipFile
from io import BytesIO
import platform
import requests
import json

# Function to check if a library is installed
def check_and_install(package):
    try:
        __import__(package)
        print(f"{package} is already installed.")
    except ImportError:
        response = input(f"{package} is not installed. Would you like to install it now? (yes/no): ").strip().lower()
        if response == 'yes':
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} installed successfully.")
        else:
            print(f"{package} is required. Exiting the script.")
            sys.exit(1)

# Check and install required libraries
required_libraries = ['requests', 'protobuf']
for lib in required_libraries:
    check_and_install(lib)

# Function to check if protoc is installed
def check_protoc_installed():
    protoc_path = shutil.which("protoc")
    
    if protoc_path:
        print(f"protoc is already installed and available at {protoc_path}.")
        return protoc_path
    
    # Check if protoc is in the bin directory of the current script
    local_protoc_path = os.path.join(os.getcwd(), 'bin', 'protoc.exe')
    if os.path.isfile(local_protoc_path):
        print(f"protoc found in local bin directory: {local_protoc_path}.")
        os.environ["PATH"] += os.pathsep + os.path.abspath(os.path.dirname(local_protoc_path))
        return local_protoc_path
    
    # If not found, prompt to download and install
    print("protoc is not installed or not available in the system's PATH.")
    response = input("Would you like to download and install protoc from the GitHub releases page? (yes/no): ").strip().lower()
    if response == 'yes':
        return download_and_install_protoc()
    else:
        print("protoc is required. Exiting the script.")
        sys.exit(1)

# Function to download and install protoc
def download_and_install_protoc():
    latest_release_api_url = "https://api.github.com/repos/protocolbuffers/protobuf/releases/latest"
    response = requests.get(latest_release_api_url)
    release_data = response.json()

    available_assets = []
    print("Available protoc versions:")

    for asset in release_data['assets']:
        if asset['name'].endswith('.zip'):
            available_assets.append((release_data['tag_name'], asset['name'], asset['browser_download_url']))
    
    if not available_assets:
        print(f"No compatible protoc version found. Exiting.")
        sys.exit(1)

    for idx, (tag_name, asset_name, _) in enumerate(available_assets, start=1):
        print(f"{idx}: {tag_name} - {asset_name}")

    version_choice = int(input("Enter the number of the version you want to download: ")) - 1
    selected_tag, selected_asset, download_url = available_assets[version_choice]

    print(f"Downloading {selected_tag} for {selected_asset}...")
    response = requests.get(download_url)
    with ZipFile(BytesIO(response.content)) as zip_file:
        zip_file.extractall('bin')

    folder = 'bin'
    local_protoc_path = os.path.join(folder, 'protoc.exe')
    if os.path.isfile(local_protoc_path):
        print('protoc installed successfully.')
        os.environ["PATH"] += os.pathsep + os.path.abspath(folder)
        print(f'Updated PATH: {os.environ["PATH"]}')
        print("You may need to restart your shell or add the path manually to your system's PATH environment variable.")
        return local_protoc_path
    else:
        print('Failed to install protoc.')
        sys.exit(1)

# Check if protoc is installed
protoc_path = check_protoc_installed()

# Step 1: Retrieve the OpenAPI JSON from the provided URL
url = 'https://api.ptvgroup.tech/meta/services/mlf/v1/openapi.json'
response = requests.get(url)
openapi_json = response.json()

# Debug: Print the structure of the OpenAPI JSON
#print(json.dumps(openapi_json, indent=4))

# Step 2: Extract the protobuf file content from the description attribute
protobuf_content = None

# Assuming the structure of the OpenAPI JSON to find the relevant description
for schema_name, schema_info in openapi_json['components']['schemas'].items():
    if 'description' in schema_info and 'proto definition:' in schema_info['description'].lower():
        description = schema_info['description']
        start_index = description.lower().index('proto definition:')
        protobuf_content = description[start_index + len('proto definition:'):].strip()
        break

if not protobuf_content:
    raise ValueError("Protobuf content not found in the OpenAPI JSON description.")

# Step 3: Save the extracted protobuf content locally
proto_file_path = './street_forecast.proto'
with open(proto_file_path, 'w') as proto_file:
    proto_file.write(protobuf_content)

# Step 4: Use the `protoc` tool to compile the protobuf file
protoc_command = f'"{protoc_path}" --python_out=. {proto_file_path}'
os.system(protoc_command)

print("Protobuf file compiled successfully.")
