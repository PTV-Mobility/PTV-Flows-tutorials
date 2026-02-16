import requests
import dataprv_traffic_realtime_data_pb2
from google.protobuf.timestamp_pb2 import Timestamp

# URL of your GET request
url = "https://api.ptvgroup.tech/flows/realtime-traffic/v1/realtime/traffic"

# Configure your API key here
api_key = "put your API key here"

# Set up the headers with the 'apiKey'
headers = {
    'apiKey': api_key
}

# Make the GET request with the headers
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Get the binary content
    data = response.content

    # Parse the protobuf message
    message = dataprv_traffic_realtime_data_pb2.DataprvTrafficRealtimeDataProto()
    message.ParseFromString(data)

    # Access the parsed data
    print("Timezone:", message.timezone)
    print("Snapshot DateTime:", message.snapshot_date_time.ToDatetime())

    for street in message.street_traffic:
        print("Street ID:", street.id)
        print("From Node ID:", street.from_node_id)
        print("Speed (km/h):", street.speed_kmh)
#print("Probe Count:", street.probe_count)
        print("OLR Code:", street.olr_code)
        print("-" * 20)
else:
    print("Failed to retrieve data. Status code:", response.status_code)