# PTV Flows Realtime API - Python Tutorial

This tutorial demonstrates how to fetch and monitor real-time traffic data from the PTV Flows API, with various filtering and export options.

## 🚀 Quick Start

1. **Setup Environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   python setup.py
   ```

2. **Run Example**:
   ```bash
   python example.py
   ```

3. **Fetch Real-time Data**:
   ```bash
   python ptv_flows_realtime.py --api-key YOUR_API_KEY
   ```

4. **Monitor Traffic Changes**:
   ```bash
   python ptv_flows_realtime_monitor.py --api-key YOUR_API_KEY
   ```

## ✨ Features

- **Secure API key handling** - No hardcoded credentials
- **Interactive configuration** - User-friendly prompts for parameters
- **Multiple output formats** - CSV, JSON with structured data
- **Real-time monitoring** - Track traffic changes over time
- **Flexible filtering** - Filter by speed, street IDs, and more
- **Production & staging support** - Choose your environment
- **Comprehensive logging** - Detailed progress and error information
- **Debug mode** - Save raw API responses for troubleshooting

## Prerequisites

- **Python 3.x** installed on your system.
- **Protocol Buffers Compiler (`protoc`)** installed and added to your system PATH.

## Setup Instructions

### 1. Create a Virtual Environment

It's recommended to use a Python virtual environment to manage dependencies.

#### On Windows

Open Command Prompt and run:

```cmd
cd %USERPROFILE%
python -m venv dataprv_env
```

Activate the virtual environment from your project directory:

```cmd
%USERPROFILE%\dataprv_env\Scripts\activate.bat
```

#### On macOS/Linux

Open Terminal and run:

```bash
cd ~
python3 -m venv dataprv_env
```

Activate the virtual environment from your project directory:

```bash
source ~/dataprv_env/bin/activate
```

### 2. Install Required Python Packages

With the virtual environment activated, install the packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

**Contents of `requirements.txt`:**

```
requests
protobuf
```

### 3. Install Protocol Buffers Compiler (`protoc`)

Download and install the `protoc` compiler appropriate for your operating system from the [Protocol Buffers Releases](https://github.com/protocolbuffers/protobuf/releases) page.

#### For Windows:

1. **Download the ZIP file**, e.g., `protoc-<version>-win64.zip`.
2. **Extract the contents** to a directory, e.g., `C:\protoc`.
3. **Add `protoc` to your PATH**:
   - Right-click on **This PC** and select **Properties**.
   - Click on **Advanced system settings**.
   - Click **Environment Variables**.
   - Under **System variables**, select **Path** and click **Edit**.
   - Click **New** and add `C:\protoc\bin`.
   - Click **OK** to save.

#### For macOS/Linux:

Use a package manager like `brew` (for macOS) or install manually.

```bash
# For macOS using Homebrew
brew install protobuf
```

Ensure `protoc` is accessible from your terminal:

```bash
protoc --version
```

### 4. Compile the Protobuf Definitions

In your project directory, compile the `.proto` files to generate Python classes.

#### Compile `dataprv_traffic_realtime_data.proto`

Ensure that all required `.proto` files are present in your project directory, including any imported files.

Run the following command:

```bash
protoc --python_out=. --proto_path=. dataprv_traffic_realtime_data.proto
```

This command generates `dataprv_traffic_realtime_data_pb2.py`, which contains the Python classes for the Protobuf messages.

**Note:** If you encounter import errors due to missing Protobuf files (e.g., `google/protobuf/timestamp.proto`), you may need to specify the include path where Protobuf's standard definitions are located.

Example:

```bash
protoc --python_out=. --proto_path=. --proto_path=PATH_TO_PROTOBUF_INCLUDE dataprv_traffic_realtime_data.proto
```

Replace `PATH_TO_PROTOBUF_INCLUDE` with the path to the `include` directory of your Protobuf installation, where the `google` folder resides.

### 5. Update the GET Request URL

In `decode_rt_protobuf_flows.py`, update the `url` variable with the actual endpoint you wish to query:

```python
# URL of your GET request
url = "https://api.ptvgroup.tech/flows/realtime-traffic/v1/realtime/traffic"
```

### 6. Run the Python Script

With the virtual environment activated and all dependencies installed, run:

```bash
python decode_rt_protobuf_flows.py
```

The script will:

- Make a GET request to the specified URL.
- Parse the binary response using the generated Protobuf classes.
- Print out the parsed traffic data.

## File Descriptions

### `decode_rt_protobuf_flows.py`

The main Python script that performs the following steps:

- Imports necessary modules:

  ```python
  import requests
  import dataprv_traffic_realtime_data_pb2
  from google.protobuf.timestamp_pb2 import Timestamp
  ```

- Sends a GET request to the specified URL.
- Checks the response status.
- Parses the binary content using the Protobuf message:

  ```python
  message = dataprv_traffic_realtime_data_pb2.DataprvTrafficRealtimeDataProto()
  message.ParseFromString(data)
  ```

- Accesses and prints the parsed data fields:

  ```python
  print("Timezone:", message.timezone)
  print("Snapshot DateTime:", message.snapshot_date_time.ToDatetime())
  ```

- Iterates over the `street_traffic` repeated field to display street-level data.

### `requirements.txt`

Lists the Python packages required to run the script:

```
requests
protobuf
```

### Protobuf Definition Files (`*.proto`)

- **`dataprv_traffic_realtime_data.proto`**: Defines the structure of the traffic data message.
- **Other `.proto` files**: May include standard Protobuf definitions required for compilation, such as:

  - `any.proto`
  - `descriptor.proto`
  - `struct.proto`
  - `type.proto`

Ensure all necessary `.proto` files are present in your project directory or accessible via the `--proto_path` option during compilation.

## Additional Notes

- **Error Handling**: If the script fails to parse the data, check that the response from the GET request matches the expected Protobuf format.
- **Protobuf Imports**: If you encounter issues with missing imports during compilation, verify that the import statements in your `.proto` files are correct and the required files are accessible.
- **Virtual Environment Activation**: Remember to activate the virtual environment each time before running the script to ensure all dependencies are available.

## Resources

- **Protocol Buffers Documentation**: [https://developers.google.com/protocol-buffers/docs/overview](https://developers.google.com/protocol-buffers/docs/overview)
- **Protobuf Python Tutorial**: [https://developers.google.com/protocol-buffers/docs/pythontutorial](https://developers.google.com/protocol-buffers/docs/pythontutorial)
- **Requests Library Documentation**: [https://requests.readthedocs.io/en/latest/](https://requests.readthedocs.io/en/latest/)
- **Python Virtual Environments**: [https://docs.python.org/3/tutorial/venv.html](https://docs.python.org/3/tutorial/venv.html)

---

If you need further assistance or encounter issues not covered in this guide, consider referring to the official documentation of the tools used or seeking help from relevant developer communities.