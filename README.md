# PTV-Flows Tutorials

A collection of tutorials for using PTV Flows, covering various tools and functionalities.

## Table of Contents
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Tutorials](#tutorials)
  - [Postman](#postman)
  - [Python](#python)
    - [Create Protobuf Street Forecast](#create-protobuf-street-forecast)
    - [Forecast decoding examples](#forecast_decoding_examples)
- [License](#license)

## Introduction

This repository contains tutorials for using PTV Flows, a powerful tool for traffic forecsat and monitoring. These tutorials provide step-by-step instructions and examples for leveraging PTV Flows in various scenarios.

## Prerequisites

- Python 3.7 or higher
- Postman installed
- Basic knowledge of Python and REST APIs

## Installation

1. Clone the repository ( or download the zip file ):
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
2. Follow the instructions in the `README.md` file inside the `postman` folder to execute the requests.

### Python

The `python` folder contains Python scripts demonstrating the usage of PTV Flows APIs. 

#### Create Protobuf Street Forecast

This script creates the protobuf street forecast .py necessary to decode the Forecast message from Flows . To run the script:

1. Navigate to the `python/create_protobuf_street_forecast` directory:
   ```bash
   cd python/create_protobuf_street_forecast
   ```
2. Run the script:
   ```bash
   python create_protobuf_street_forecast.py
   ```

#### forecast_decoding_examples

- forecast_decoding_examples.py : this script demonstrates how to download and decode a protobuf message for street forecasts. It includes functions to download a file, dynamically import the protobuf file, read the downloaded data, and decode the protobuf message.
Dependencies: Ensure that the required protobuf file (street_forecast_pb2.py) is located at the specified path.
- request_flows_forecast.py : this script demonstrates how to make a GET request to the PTV Flows API to retrieve real-time forecast data. The user is prompted to enter their PTV API key.
- Flows_client_example.py : this script mergesthe 2 previous scripts to show a simple example of a client requesting and using data from Flows

Ensure you have set up the necessary configurations as mentioned in the script comments.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
