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
required_libraries = ['requests', 'google.protobuf']
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
    system = platform.system().lower()
    if system == "windows":
        protoc_zip_url = "https://github.com/protocolbuffers/protobuf/releases/download/v21.5/protoc-21.5-win64.zip"
    elif system == "darwin":  # MacOS
        protoc_zip_url = "https://github.com/protocolbuffers/protobuf/releases/download/v21.5/protoc-21.5-osx-x86_64.zip"
    elif system == "linux":
        protoc_zip_url = "https://github.com/protocolbuffers/protobuf/releases/download/v21.5/protoc-21.5-linux-x86_64.zip"
    else:
        print(f"Unsupported system: {system}")
        sys.exit(1)

    print(f"Downloading protoc from {protoc_zip_url}...")
    response = requests.get(protoc_zip_url)
    with ZipFile(BytesIO(response.content)) as zip_file:
        zip_file.extractall("protoc")

    protoc_path = os.path.join(os.getcwd(), 'protoc', 'bin', 'protoc')
    os.environ["PATH"] += os.pathsep + os.path.abspath(os.path.dirname(protoc_path))
    print(f"protoc installed successfully at {protoc_path}.")
    return protoc_path


# Import the generated Python modules
'''
import flows_network_v1_pb2 as flows_network

# Example usage of the generated classes
def example_usage():
    # Create a new Network message
    network = flows_network.Network()
    network.map_version = "v1.0"
    network.coordinate_reference_system = "WGS-84"

    # Create a new Street message and add it to the Network
    street = network.street.add()
    street.id = 123
    street.from_node_id = 456
    street.openlr = b"\x01\x02\x03"
    street.functional_road_class = 2
    street.form_of_way = 1
    street.free_flow_speed_kmph = 60.0
    street.shape = b"\x04\x05\x06"
    street.name = "Main Street"

    # Serialize the Network message to a binary string
    serialized_data = network.SerializeToString()

    # Deserialize the binary string to a new Network message
    new_network = flows_network.Network()
    new_network.ParseFromString(serialized_data)

    # Print the deserialized message
    print(new_network)
'''

if __name__ == "__main__":
    #example_usage()
    print(" Check if protoc is installed")
    protoc_path = check_protoc_installed()

    # Path to the .proto file
    proto_file = 'flows_network_v1.proto'
    print("Generate Python code from the .proto file")
    # Generate Python code from the .proto file
    subprocess.run([protoc_path, '--python_out=.', '--proto_path=.', proto_file], check=True)
