import requests
import json
import sys
import os
from tqdm import tqdm
import urllib.request
import importlib.util

# Add the current working directory to the system path
sys.path.append(os.getcwd())

# URL to download the data file
url = 'https://ptv2box.ptvgroup.com/index.php/s/RL5wACTDjsqRM4S/download?path=%2F&files='
file_name = 'response_protobuf_mlf_forecast_example'
end_url = url + file_name

# Function to download a file with progress bar
def download_file(url, dest):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    t = tqdm(total=total_size, unit='B', unit_scale=True, desc=dest, ncols=100)
    with open(dest, 'wb') as file:
        for data in response.iter_content(block_size):
            t.update(len(data))
            file.write(data)
    t.close()

# Download the data file
print("Downloading data file IN REALITY YOU SHOULD CALL THE PTV FLOWS FORECAST API...")
download_file(end_url, file_name)

# Path to the protobuf file
file_path = '../create_protobuf_street_forecast/street_forecast_pb2.py'

# Dynamically import the protobuf file
spec = importlib.util.spec_from_file_location("mlf_protobuf_pb2", file_path)
mlf_protobuf_pb2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mlf_protobuf_pb2)

# Read the downloaded data file
print("Reading the downloaded data file...")
with open(file_name, 'rb') as f:
    message_data = f.read()

# Decode the protobuf message
print("Decoding the protobuf message...")
forecast_data = mlf_protobuf_pb2.ForecastData()
forecast_data.ParseFromString(message_data)

# Access the first element in the array of results
if forecast_data.streetForecast:
    first_street_forecast = forecast_data.streetForecast[0]
    if first_street_forecast.forecast:
        first_forecast = first_street_forecast.forecast[0]
        # Print the first forecast
        print("First forecast data:")
        print(first_forecast)
    else:
        print("No forecasts available in the first street forecast.")
else:
    print("No street forecasts available.")

# Identifiers of the road link
road_link_info = (forecast_data.streetForecast[0].id, forecast_data.streetForecast[0].fromNode)
openLR_code = forecast_data.streetForecast[0].openLRcode
print(f"Identifiers of the road link: {road_link_info} OR OpenLR code: {openLR_code}")

# The whole forecast for the first street
print("Whole forecast for the first street:")
print(forecast_data.streetForecast[0].forecast)

# Current speed estimation
current_speed_estimation = forecast_data.streetForecast[0].forecast[0]
print(f"Current speed estimation: {current_speed_estimation}")

# Number of links with forecast
num_links_with_forecast = len(forecast_data.streetForecast)
print(f"Number of links with forecast: {num_links_with_forecast}")

# Current timestamp of the first forecast
current_timestamp = forecast_data.streetForecast[0].forecast[0].start
print(f"Current timestamp of the first forecast: {current_timestamp}")

# Store a new list with just the forecast at +0m (initial forecast)
current_speeds = {}
road_links = len(forecast_data.streetForecast)
for street in forecast_data.streetForecast:
    stridx = '{}_{}'.format(street.id, street.fromNode)
    current_speeds[stridx] = street.forecast[0].speed

# Calculate the size of the forecast data
size_in_bytes = sys.getsizeof(current_speeds)
size_in_kb = size_in_bytes / 1024
oneday_size_mb = (12 * 24 * size_in_kb / 1024.0)
onemonth_gb = (oneday_size_mb * 30 / 1024.0)
oneyear_gb = 365 * oneday_size_mb / 1024.0
road_links = len(forecast_data.streetForecast)

# Print the size information
print(f"The size of a single forecast horizon for this instance is {size_in_kb:.2f} KB for {road_links} road links")
print(f"For one day you will need {oneday_size_mb:.2f} MegaB")
print(f"For one month you will need {onemonth_gb:.2f} GigaB")
print(f"For one year you will need {oneyear_gb:.2f} GigaB")

# Import the dictionary into a pandas dataframe for analysis
#import pandas as pd

#df = pd.DataFrame.from_dict(current_speeds, orient='index', columns=['speed'])
#df.index.name = 'id_fromNode'

# Display the dataframe
#print("Dataframe of current speeds:")
#print(df)
