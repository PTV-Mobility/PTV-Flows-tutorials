# filename: monitor_rt_protobuf_flows.py

import requests
import dataprv_traffic_realtime_data_pb2
from google.protobuf.timestamp_pb2 import Timestamp
import time
import hashlib
import json

# URL of your GET request
url = "https://api.ptvgroup.tech/flows/realtime-traffic/v1/realtime/traffic"

# Configure your API key here
api_key = "put your API key here"

# Set up the headers with the 'apiKey'
headers = {
    'apiKey': api_key
}

# Initialize variables
prev_data = None  # Holds the data from the previous payload
prev_snapshot_time = None  # Holds the snapshot time of the previous payload
difference_info = []  # List to hold difference counts and snapshot times
max_call = 100
previous_hash = None  # Initialize previous hash

for i in range(max_call):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.content

        # Decode the Protobuf message
        message = dataprv_traffic_realtime_data_pb2.DataprvTrafficRealtimeDataProto()
        message.ParseFromString(data)

        # Extract the snapshot_date_time
        snapshot_time = message.snapshot_date_time.ToDatetime()

        # Extract and sort the street_traffic data by olr_code for deterministic ordering
        street_traffic_list = sorted(
            message.street_traffic, key=lambda x: x.olr_code
        )

        # Serialize the street_traffic data into a consistent JSON string
        street_traffic_serialized = json.dumps([
            {
                'id': street.id,
                'from_node_id': street.from_node_id,
                'speed_kmh': street.speed_kmh,
                'probe_count': street.probe_count,
                'olr_code': street.olr_code
            }
            for street in street_traffic_list
        ], sort_keys=True)

        # Calculate the SHA256 hash of the serialized street_traffic data
        current_hash = hashlib.sha256(street_traffic_serialized.encode('utf-8')).hexdigest()
        print(f"Call {i + 1}: StreetTraffic Hash = {current_hash}")

        # Compare with the previous hash
        if previous_hash == current_hash:
            print("No changes in the payload.\n")
        else:
            if previous_hash is not None:
                print("Payload has changed. Processing data...")

            previous_hash = current_hash

            # Build a dictionary of olr_code to street info
            current_data = {}
            for street in street_traffic_list:
                olr_code = street.olr_code
                speed_kmh = street.speed_kmh
                # Collect other info if needed
                street_info = {
                    'street_id': street.id,
                    'from_node_id': street.from_node_id,
                    'speed_kmh': speed_kmh,
                    'probe_count': street.probe_count,
                    'olr_code': olr_code,
                    'snapshot_time': snapshot_time
                }
                current_data[olr_code] = street_info

            # Print the call index and timestamp
            print(f"Call {i + 1} at {snapshot_time}")

            # If prev_data is not None, compare current_data to prev_data
            if prev_data is not None:
                differences = 0  # Counter for streets that differ
                example_printed = 0  # Counter for examples printed

                for olr_code, street_info in current_data.items():
                    if olr_code in prev_data:
                        prev_speed = prev_data[olr_code]['speed_kmh']
                        curr_speed = street_info['speed_kmh']
                        # If speeds are different, increment the counter
                        if prev_speed != curr_speed:
                            differences += 1
                            # Print details for the first two differences
                            if example_printed < 2:
                                print("\nDifference Details:")
                                print(f"OLR Code: {olr_code}")
                                print(f"Street ID: {street_info['street_id']}")
                                print(f"From Node ID: {street_info['from_node_id']}")
                                print(f"Speed at {prev_data[olr_code]['snapshot_time']}: {prev_speed} km/h")
                                print(f"Speed at {street_info['snapshot_time']}: {curr_speed} km/h")
                                example_printed += 1

                # Store the differences along with snapshot times
                difference_info.append({
                    'prev_snapshot_time': prev_snapshot_time,
                    'curr_snapshot_time': snapshot_time,
                    'differences': differences
                })
                print(f"Number of streets with differing speeds compared to previous call: {differences}\n")
            else:
                # For the first processed payload, we have no previous data to compare
                print("No previous data to compare.\n")

            # Update prev_data and prev_snapshot_time
            prev_data = current_data
            prev_snapshot_time = snapshot_time
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
        exit(1)

    if i < (max_call - 1):
        # Wait for 1 minute before next call
        time.sleep(60)

# After all fetches are complete, print the summary counts
print("=== Summary of Differences ===")
for idx, info in enumerate(difference_info, start=1):
    prev_time = info['prev_snapshot_time']
    curr_time = info['curr_snapshot_time']
    count = info['differences']
    print(f"Between Call {idx} ({prev_time}) and Call {idx + 1} ({curr_time}): {count} streets differed in speed.")

# If you want to exit with a message if no differences were found at all
if sum(info['differences'] for info in difference_info) == 0:
    print("\nNo differences in speed were found between any of the calls.")