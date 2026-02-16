#!/usr/bin/env python3
"""
PTV Flows Realtime API - Quick Start Example

This example demonstrates basic usage of the PTV Flows Realtime API client.
It fetches real-time traffic data and saves it in both CSV and JSON formats.

Run this example to test your API key and get familiar with the basic functionality.
"""

import os
import sys
import logging

# Configure logging for the example
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_example():
    """Run the basic realtime API example."""
    
    print("PTV Flows Realtime API - Quick Start Example")
    print("=" * 50)
    print()
    
    # Check if protobuf files exist
    if not os.path.exists("dataprv_traffic_realtime_data_pb2.py"):
        print("❌ Error: Required protobuf file not found!")
        print("   Make sure 'dataprv_traffic_realtime_data_pb2.py' is in the same directory.")
        print("   If you're missing this file, check the project documentation.")
        return False
    
    try:
        # Import the main realtime module
        from ptv_flows_realtime import (
            fetch_realtime_data, 
            parse_protobuf_data, 
            filter_traffic_data,
            save_to_csv,
            save_to_json
        )
        
        # Configuration
        print("Configuration:")
        print("- Using staging environment (safer for testing)")
        print("- Output format: Both CSV and JSON")
        print("- No data filtering (all records)")
        print()
        
        # Use staging endpoint for example
        endpoint = "https://api.ptvgroup.tech/flows/realtime-traffic/v1/realtime/traffic"
        api_key = "change_me_to_your_api_key"
        
        if api_key == "change_me_to_your_api_key":
            print("🔑 To run this example with real data:")
            print("   1. Get your API key from: https://ptvgroup.tech/flows/")
            print("   2. Replace 'change_me_to_your_api_key' in this script")
            print("   3. Or use: python ptv_flows_realtime.py --api-key YOUR_API_KEY")
            print()
            print("This example will show you the expected workflow, but will fail without a valid API key.")
            print()
            
            response = input("Continue with example workflow demonstration? (y/N): ")
            if response.lower() != 'y':
                print("Example cancelled.")
                return False
        
        # Create example output directory
        output_dir = "example_output"
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Fetching real-time traffic data from staging API...")
        print(f"Endpoint: {endpoint}")
        
        try:
            # Fetch data
            raw_data = fetch_realtime_data(api_key, endpoint, debug=False)
            
            # Parse data
            print("Parsing protobuf data...")
            message = parse_protobuf_data(raw_data)
            
            # Extract and filter data (no filters for example)
            print("Processing traffic data...")
            traffic_data = filter_traffic_data(message, {})
            
            print(f"✅ Successfully processed {len(traffic_data)} traffic records")
            
            # Save data in both formats
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            csv_path = os.path.join(output_dir, f"example_realtime_{timestamp}.csv")
            json_path = os.path.join(output_dir, f"example_realtime_{timestamp}.json")
            
            print("Saving data...")
            save_to_csv(traffic_data, csv_path)
            save_to_json(traffic_data, json_path)
            
            print()
            print("✅ Example completed successfully!")
            print(f"Output files saved in: {output_dir}/")
            print(f"  - CSV: {os.path.basename(csv_path)}")
            print(f"  - JSON: {os.path.basename(json_path)}")
            
            # Display sample data
            if traffic_data:
                print()
                print("Sample of first 3 records:")
                for i, record in enumerate(traffic_data[:3]):
                    print(f"  {i+1}. Street ID: {record['street_id']}, Speed: {record['speed_kmh']} km/h")
                
                if len(traffic_data) > 3:
                    print(f"  ... and {len(traffic_data) - 3} more records")
            
            print()
            print("Next steps:")
            print("  - Try the full script: python ptv_flows_realtime.py --help")
            print("  - Monitor changes: python ptv_flows_realtime_monitor.py --help")
            print("  - Check the README.md for more options")
            
            return True
            
        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                print("❌ Authentication error - Invalid API key")
                print("   Please check your API key and try again.")
            else:
                print(f"❌ Error during example execution: {e}")
            
            print()
            print("This is expected if you haven't set up a valid API key yet.")
            print("The example shows the workflow - replace the API key to get real data.")
            
            return False
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all required files are present and dependencies are installed.")
        print("   Try running: python setup.py")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function for the example."""
    try:
        success = run_example()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nExample cancelled by user.")
        sys.exit(1)

if __name__ == "__main__":
    main()