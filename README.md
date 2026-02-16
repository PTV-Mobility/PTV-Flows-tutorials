# PTV-Flows Tutorials

A collection of tutorials for using PTV Flows, covering various tools and functionalities, provided by the PTV Flows community.
ATTENTION: these examples are not officially maintained by PTV, and no support is provided or granted. They are intended solely as illustrative, community‑driven samples to help you understand possible integrations and workflows with PTV Flows. Use them as inspiration or starting points, but always validate and adapt the code to your own environment and requirements. 

## Table of Contents
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Tutorials](#tutorials)
  - [Postman](#postman)
  - [Microsoft BI for Flows](#microsoft-bi-for-flows)
  - [Excel Example](#excel-example)
  - [Python](#python)
    - [Historical Data API (HDA) Tutorial](#historical-data-api-hda-tutorial) 🆕
    - [Create Protobuf Street Forecast](#create-protobuf-street-forecast)
    - [Create Protobuf Street Network](#create-protobuf-street-network)
    - [Forecast Decoding Examples](#forecast-decoding-examples)
    - [PTV Flows Network Downloader](#ptv-flows-network-downloader)
- [License](#license)

## Introduction

This repository contains tutorials for using PTV Flows, a powerful tool for traffic forecast and monitoring. These tutorials provide step-by-step instructions and examples for leveraging PTV Flows in various scenarios.

## Prerequisites

- Python 3.7 or higher
- Postman installed
- Microsoft Excel (for the Excel example)
- Basic knowledge of Python and REST APIs

## Installation

1. Clone the repository (or download the zip file):
   ```bash
   git clone https://github.com/PTV-Mobility/PTV-Flows-tutorials.git
   ```
2. Navigate to the project directory:
   ```bash
   cd PTV-Flows-tutorials
   ```

## Tutorials

### Postman

The `postman` folder contains Postman collections and environments for interacting with PTV Flows APIs. To use these:

1. Import the collections and environments into Postman.
2. Follow the instructions in the [`postman/README.md`](postman/README.md) file to execute the requests.

### Microsoft BI for Flows

The `MICROSOFT BI FOR FLOWS` folder contains BI dashboard examples that connect to the PTV Flows API using Microsoft Power BI.

- Follow the instructions in the [`MICROSOFT BI FOR FLOWS/README.md`](MICROSOFT%20BI%20FOR%20FLOWS/README.md) file to get started.

### Excel Example

The `excel` folder contains an Excel file and related instructions that demonstrate how to retrieve existing KPIs and query the Historical Data Analysis (HDA) module of PTV Flows.

- **File:** `20250131 HDA Heatmap Example.xlsx`
- **Instructions:**
  - Refer to the [`excel/README.md`](excel/README.md) file for detailed steps on how to use the Excel file.

### Python

The `python` folder contains Python scripts demonstrating the usage of PTV Flows APIs. 

#### Historical Data API (HDA) Tutorial 🆕

**[UNDER CONSTRUCTION - Phase 1 Complete]**

The `python/hda api/` folder contains a comprehensive tutorial for using the PTV Flows Historical Data API. This tutorial provides access to traffic statistics, KPI monitoring, time series analysis, and network performance data.

**Features:**
- Complete Python client for all 9 HDA API endpoints
- Interactive examples and demonstrations
- Multiple output formats (JSON, Parquet, CSV)
- Statistical analysis and visualization capabilities
- Automated setup and dependency management

**Quick Start:**
```bash
cd "python/hda api"
python setup.py          # Install dependencies
python example.py         # Run interactive tutorial
```

**Status:**
- ✅ Phase 1: Core infrastructure complete
- 🔄 Phase 2: Advanced analysis scripts (planned)
- ⏸️ Phase 3: Testing and final polish (planned)

See [`python/hda api/README.md`](python/hda%20api/README.md) for detailed documentation.

#### Create Protobuf Street Forecast

This script creates the Protobuf street forecast `.py` file (`street_forecast_pb2.py`) necessary to decode the forecast messages from PTV Flows.

**Instructions:**

1. Navigate to the `python/create_protobuf_street_forecast` directory:
   ```bash
   cd python/create_protobuf_street_forecast
   ```
2. Run the script:
   ```bash
   python create_protobuf_street_forecast.py
   ```

#### Create Protobuf Street Network

This script creates the Protobuf street network `.py` file (`flows_network_v1_pb2.py`) necessary to decode the network messages from PTV Flows.

**Instructions:**

1. Navigate to the `python/create_protobuf_street_network` directory:
   ```bash
   cd python/create_protobuf_street_network
   ```
2. Run the script:
   ```bash
   python create_protobuf_street_network.py
   ```

#### Forecast Decoding Examples

The `forecast_decoding_examples` folder contains scripts that demonstrate how to request and decode forecast data from PTV Flows.

**Files:**

- `forecast_decoding_examples.py`: Demonstrates how to download and decode a Protobuf message for street forecasts.

- `request_flows_forecast.py`: Demonstrates how to make a GET request to the PTV Flows API to retrieve real-time forecast data.

- `Flows_client_example.py`: Combines the functionality of the previous scripts to show a simple client example.

**Usage:**

1. Ensure that you have generated the required Protobuf Python files (`street_forecast_pb2.py`, `flows_network_v1_pb2.py`).

2. Run the example scripts as needed:
   ```bash
   python forecast_decoding_examples.py
   ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
 ## PTV Flows Network Downloader (python/network api/ptv_flows_downloader.py)

 The `ptv_flows_downloader.py` script downloads the PTV Flows street network protobuf message, optionally filters it by a bounding box, and exports the result to CSV and TopoJSON.

 Usage examples:

 - Download using an environment variable for the API key and interactively provide a bbox:

 ```bash
 export PTV_API_KEY="your_api_key_here"
 python "python/network api/ptv_flows_downloader.py"
 ```

 - Provide a bbox on the command line (min_lon,min_lat,max_lon,max_lat):

 ```bash
 python "python/network api/ptv_flows_downloader.py" --bbox="2.3,48.8,2.4,48.9" --output-dir=out
 ```

 - Skip bounding-box filtering and process the entire network (may be large and memory/time intensive):

 ```bash
 python "python/network api/ptv_flows_downloader.py" --no-filter --output-dir=out
 ```

 Notes:
 - If neither `--bbox` nor `--no-filter` are provided the script will prompt for a bounding box interactively.
 - For large areas or `--no-filter`, ensure you have sufficient disk space and memory.
