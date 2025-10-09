#!/usr/bin/env python3
"""
PTV Flows Realtime API Client

This script fetches real-time traffic data from PTV Flows API and provides various
export options including CSV and JSON formats.

Usage:
    python ptv_flows_realtime.py [--api-key API_KEY] [--output-dir OUTPUT_DIR] [--format FORMAT]

Author: Refactored from decode_rt_protobuf_flows.py for better security and usability
"""

import argparse
import sys
import os
import json
import csv
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

import requests
import dataprv_traffic_realtime_data_pb2
from google.protobuf.timestamp_pb2 import Timestamp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_api_endpoint_from_user() -> str:
    """
    Prompts the user to choose API environment.
    
    Returns:
        Selected API endpoint URL
    """
    print("Please select the API environment:")
    print("1. Production: https://api.ptvgroup.tech/flows/realtime-traffic/v1/realtime/traffic")
    print("2. Staging: https://api.ptvgroup.tech/flows/realtime-traffic/v1/realtime/traffic")
    
    while True:
        try:
            choice = input("Enter your choice (1 or 2): ").strip()
            
            if choice == "1":
                return "https://api.ptvgroup.tech/flows/realtime-traffic/v1/realtime/traffic"
            elif choice == "2":
                return "https://api.ptvgroup.tech/flows/realtime-traffic/v1/realtime/traffic"
            else:
                print("Invalid choice. Please enter 1 or 2.")
                
        except (ValueError, KeyboardInterrupt):
            print("\nOperation cancelled by user")
            sys.exit(1)


def fetch_realtime_data(api_key: str, endpoint: str, debug: bool = False) -> bytes:
    """
    Fetches real-time traffic data from PTV Flows API.
    
    Args:
        api_key: PTV API key
        endpoint: API endpoint URL
        debug: Whether to save raw response data
        
    Returns:
        Raw protobuf data as bytes
    """
    headers = {
        'apiKey': api_key
    }
    
    logger.info(f"Fetching data from {endpoint}")
    
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        
        if debug:
            # Save raw response to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_file = f"realtime_data_raw_{timestamp}.bin"
            with open(debug_file, "wb") as f:
                f.write(response.content)
            logger.info(f"Saved raw data to {debug_file}")
        
        logger.info(f"Successfully fetched {len(response.content)} bytes of data")
        return response.content
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        if response.status_code == 401:
            logger.error("Authentication failed. Please check your API key.")
        elif response.status_code == 403:
            logger.error("Access forbidden. Please check your API key permissions.")
        raise


def parse_protobuf_data(data: bytes) -> dataprv_traffic_realtime_data_pb2.DataprvTrafficRealtimeDataProto:
    """
    Parses the protobuf message from binary data.
    
    Args:
        data: Raw protobuf data
        
    Returns:
        Parsed protobuf message
    """
    try:
        message = dataprv_traffic_realtime_data_pb2.DataprvTrafficRealtimeDataProto()
        message.ParseFromString(data)
        logger.info("Successfully parsed protobuf data")
        return message
        
    except Exception as e:
        logger.error(f"Error parsing protobuf data: {e}")
        raise


def filter_traffic_data(message, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filters and extracts traffic data based on provided filters.
    
    Args:
        message: Parsed protobuf message
        filters: Dictionary containing filter criteria
        
    Returns:
        List of filtered street traffic data
    """
    street_data = []
    
    min_speed = filters.get('min_speed')
    max_speed = filters.get('max_speed')
    street_ids = filters.get('street_ids', [])
    
    logger.info(f"Processing {len(message.street_traffic)} street records")
    
    for street in message.street_traffic:
        # Apply filters
        if min_speed is not None and street.speed_kmh < min_speed:
            continue
        if max_speed is not None and street.speed_kmh > max_speed:
            continue
        if street_ids and street.id not in street_ids:
            continue
            
        street_record = {
            'street_id': street.id,
            'from_node_id': street.from_node_id,
            'speed_kmh': street.speed_kmh,
            'olr_code': street.olr_code,
            'timestamp': message.snapshot_date_time.ToDatetime().isoformat() if message.snapshot_date_time else None,
            'timezone': message.timezone if hasattr(message, 'timezone') else None
        }
        
        # Add probe count if available
        if hasattr(street, 'probe_count'):
            street_record['probe_count'] = street.probe_count
            
        street_data.append(street_record)
    
    logger.info(f"Filtered to {len(street_data)} records")
    return street_data


def save_to_csv(data: List[Dict[str, Any]], output_path: str):
    """
    Saves traffic data to CSV format.
    
    Args:
        data: List of traffic records
        output_path: Output file path
    """
    if not data:
        logger.warning("No data to save to CSV")
        return
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(data)
            
        logger.info(f"Saved {len(data)} records to {output_path}")
        
    except Exception as e:
        logger.error(f"Error saving CSV: {e}")
        raise


def save_to_json(data: List[Dict[str, Any]], output_path: str):
    """
    Saves traffic data to JSON format.
    
    Args:
        data: List of traffic records
        output_path: Output file path
    """
    if not data:
        logger.warning("No data to save to JSON")
        return
    
    try:
        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
            
        logger.info(f"Saved {len(data)} records to {output_path}")
        
    except Exception as e:
        logger.error(f"Error saving JSON: {e}")
        raise


def get_filtering_options() -> Dict[str, Any]:
    """
    Prompts user for filtering options.
    
    Returns:
        Dictionary containing filter criteria
    """
    filters = {}
    
    print("\n=== Data Filtering Options ===")
    print("Press Enter to skip any filter")
    
    try:
        # Speed filters
        min_speed_input = input("Minimum speed (km/h): ").strip()
        if min_speed_input:
            filters['min_speed'] = float(min_speed_input)
            
        max_speed_input = input("Maximum speed (km/h): ").strip()
        if max_speed_input:
            filters['max_speed'] = float(max_speed_input)
            
        # Street ID filter
        street_ids_input = input("Street IDs (comma-separated): ").strip()
        if street_ids_input:
            filters['street_ids'] = [id.strip() for id in street_ids_input.split(',')]
            
        if filters:
            logger.info(f"Applied filters: {filters}")
        else:
            logger.info("No filters applied")
            
    except ValueError as e:
        logger.warning(f"Invalid filter input: {e}")
        
    return filters


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Fetch and process PTV Flows real-time traffic data')
    parser.add_argument('--api-key', type=str,
                       help='PTV API key (if not provided, will use default placeholder)')
    parser.add_argument('--endpoint', type=str,
                       help='API endpoint URL (if not provided, will prompt user)')
    parser.add_argument('--output-dir', type=str, default='.',
                       help='Output directory for files (default: current directory)')
    parser.add_argument('--format', type=str, choices=['csv', 'json', 'both'], default='both',
                       help='Output format (default: both)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode (saves raw downloaded data)')
    parser.add_argument('--no-filter', action='store_true',
                       help='Skip interactive filtering options')
    
    args = parser.parse_args()
    
    # Handle API key
    default_api_key = "change_me_to_your_api_key"
    api_key = args.api_key or default_api_key
    
    if api_key == default_api_key:
        logger.warning("Using default placeholder API key. Please provide your actual API key using --api-key")
        logger.warning("Get your API key from: https://ptvgroup.tech/flows/")
    
    # Handle endpoint
    endpoint = args.endpoint or get_api_endpoint_from_user()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        # Fetch real-time data
        logger.info("Fetching real-time traffic data...")
        data = fetch_realtime_data(api_key, endpoint, debug=args.debug)
        
        # Parse protobuf data
        logger.info("Parsing protobuf data...")
        message = parse_protobuf_data(data)
        
        # Get filtering options
        filters = {} if args.no_filter else get_filtering_options()
        
        # Filter and extract data
        logger.info("Processing traffic data...")
        traffic_data = filter_traffic_data(message, filters)
        
        if not traffic_data:
            logger.error("No traffic data found matching the criteria. Exiting.")
            sys.exit(1)
        
        # Generate output file names
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save in requested formats
        if args.format in ['csv', 'both']:
            csv_path = os.path.join(args.output_dir, f"ptv_flows_realtime_{timestamp}.csv")
            logger.info("Saving to CSV...")
            save_to_csv(traffic_data, csv_path)
        
        if args.format in ['json', 'both']:
            json_path = os.path.join(args.output_dir, f"ptv_flows_realtime_{timestamp}.json")
            logger.info("Saving to JSON...")
            save_to_json(traffic_data, json_path)
        
        logger.info("Processing completed successfully!")
        logger.info(f"Processed {len(traffic_data)} traffic records")
        
        # Display summary statistics
        if traffic_data:
            speeds = [record['speed_kmh'] for record in traffic_data]
            logger.info(f"Speed statistics - Min: {min(speeds):.1f} km/h, Max: {max(speeds):.1f} km/h, Avg: {sum(speeds)/len(speeds):.1f} km/h")
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()