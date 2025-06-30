import requests
import sys
import os
import importlib.util
from datetime import datetime
import logging
#import pandas as pd  # Import pandas for later use

# Constants
API_KEY_PROMPT = "Please enter your PTV API key: "
API_URL = "https://api.ptvgroup.tech/mlf/v1/forecast/realtime"
FILE_PATH = '../create_protobuf_street_forecast/street_forecast_pb2.py'

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_protobuf_module(file_path: str) -> object:
    """Dynamically import the protobuf module from the given file path."""
    spec = importlib.util.spec_from_file_location("mlf_protobuf_pb2", file_path)
    mlf_protobuf_pb2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mlf_protobuf_pb2)
    return mlf_protobuf_pb2

def convert_timestamp(timestamp: object) -> str:
    """Convert a timestamp to a readable datetime format."""
    if isinstance(timestamp, int):
        return datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S UTC')
    elif hasattr(timestamp, 'seconds') and hasattr(timestamp, 'nanos'):
        # timestamp is a Timestamp object
        return datetime.utcfromtimestamp(timestamp.seconds + timestamp.nanos / 1e9).strftime('%Y-%m-%d %H:%M:%S.%f UTC')
    else:
        raise ValueError("Unsupported timestamp type")

def safe_get(data: dict, *keys: str) -> any:
    """Safely get nested dictionary or list values."""
    for key in keys:
        if data is None:
            return None
        if isinstance(data, (list, tuple)):
            if isinstance(key, int) and 0 <= key < len(data):
                data = data[key]
            else:
                return None
        elif isinstance(data, dict):
            data = data.get(key)
        else:
            return None
    return data

def get_api_response(api_key: str) -> requests.Response:
    """Send a GET request to the API and return the response."""
    try:
        response = requests.get(f"{API_URL}?apiKey={api_key}")
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logger.error(f"Error occurred while making the request: {e}")
        sys.exit(1)

def parse_forecast_data(response: requests.Response) -> object:
    """Parse the forecast data from the API response."""
    try:
        mlf_protobuf_pb2 = load_protobuf_module(FILE_PATH)
        forecast_data = mlf_protobuf_pb2.ForecastData()
        forecast_data.ParseFromString(response.content)
        return forecast_data
    except Exception as e:
        logger.error(f"Error parsing protobuf message: {e}")
        sys.exit(1)

def analyze_forecast_data(forecast_data: object) -> dict:
    """Analyze the forecast data and return a dictionary with results."""
    num_links_with_forecast = len(forecast_data.streetForecast)
    current_speeds = {}
    for street in forecast_data.streetForecast:
        stridx = f"{street.id}_{street.fromNode}"
        if street.forecast:
            current_speeds[stridx] = street.forecast[0].speed

    avg_speed = sum(current_speeds.values()) / len(current_speeds)
    size_in_bytes = sys.getsizeof(current_speeds)
    size_in_kb = size_in_bytes / 1024
    oneday_size_mb = (12 * 24 * size_in_kb / 1024.0)
    onemonth_gb = (oneday_size_mb * 30 / 1024.0)
    oneyear_gb = 365 * oneday_size_mb / 1024.0

    return {
        "num_links_with_forecast": num_links_with_forecast,
        "current_speeds": current_speeds,
        "avg_speed": avg_speed,
        "size_in_kb": size_in_kb,
        "oneday_size_mb": oneday_size_mb,
        "onemonth_gb": onemonth_gb,
        "oneyear_gb": oneyear_gb
    }

def print_results(results: dict) -> None:
    """Print the analysis results."""
    logger.info(f"Number of links with forecast: {results['num_links_with_forecast']}")
    logger.info(f"Average current speed: {results['avg_speed']:.2f}")
    logger.info(f"Size information:")
    logger.info(f"  The size of a single forecast horizon (current speed values) for this instance is {results['size_in_kb']:.2f} KB for {results['num_links_with_forecast']} road links")
    logger.info(f"  For one day you will need {results['oneday_size_mb']:.2f} MegaB")
    logger.info(f"  For one month you will need {results['onemonth_gb']:.2f} GigaB")
    logger.info(f"  For one year you will need {results['oneyear_gb']:.2f} GigaB")

def main() -> None:
    api_key = input(API_KEY_PROMPT)
    response = get_api_response(api_key)
    forecast_data = parse_forecast_data(response)
    num_links_with_forecast = len(forecast_data.streetForecast)
    logger.info(f"\nNumber of links with forecast: {num_links_with_forecast}")

    if num_links_with_forecast > 0:
        first_street = forecast_data.streetForecast[0]
        logger.info("\n1. First street forecast data:")
        logger.info(f"  ID: {first_street.id}")
        logger.info(f"  From Node: {first_street.fromNode}")
        logger.info(f"  OpenLR code: {first_street.openLRcode}")
        
        if first_street.forecast:
          logger.info("\n2. Forecasts for this street:")
          for i, forecast in enumerate(first_street.forecast):
            logger.info(f"  Forecast {i+1}:")
            logger.info(f"    Speed: {forecast.speed}")
            logger.info(f"    Start time: {datetime.utcfromtimestamp(forecast.start.seconds + forecast.start.nanos / 1e9).strftime('%Y-%m-%d %H:%M:%S.%f UTC')}")
            logger.info(f"    End time: {datetime.utcfromtimestamp(forecast.end.seconds + forecast.end.nanos / 1e9).strftime('%Y-%m-%d %H:%M:%S.%f UTC')}")
        else:
          logger.info("\n2. No forecast data available for this street.")
 

    else:
        logger.info("\nNo street forecast data available.")

    results = analyze_forecast_data(forecast_data)
    print_results(results)

    # Optional: Uncomment to use pandas for data analysis
    # df = pd.DataFrame.from_dict(results['current_speeds'], orient='index', columns=['speed'])
    # df.index.name = 'id_fromNode'
    # logger.info("\n5. Dataframe of current speeds:")
    # logger.info(df.head())  # Print first few rows

if __name__ == "__main__":
    logger.info("WARNING: You need a working PTV Flows instance with an API key enabled to use this script.")
    main()
