import requests

print("WARNING: You need a working PTV Flows instance with an API key enabled to use this script.")
# Prompt the user to enter their API key
API_KEY = input("Please enter your PTV API key: ")

# URL for the API request
url = f"https://api.ptvgroup.tech/mlf/v1/forecast/realtime?apiKey={API_KEY}"

# Empty payload and headers for the GET request
payload = {}
headers = {}

# Make the GET request to the API
print("Sending request to the API...")
response = requests.request("GET", url, headers=headers, data=payload)

# Check if the request was successful
if response.status_code == 200:
    print("Request successful! Saving response to 'forecast_response' file.")
    # Save the response content to a file as binary
    with open('forecast_response', 'wb') as file:
        file.write(response.content)
else:
    print(f"Request failed with status code: {response.status_code}")

# Optionally, print the response text (for debugging purposes)
# print(response.text)
