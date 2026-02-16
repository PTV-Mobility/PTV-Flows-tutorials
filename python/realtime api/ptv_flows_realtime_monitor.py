#!/usr/bin/env python3
"""
PTV Flows Realtime Traffic Monitor

This script continuously monitors real-time traffic data from PTV Flows API,
detects changes, and exports monitoring data with various analysis capabilities.

Usage:
    python ptv_flows_realtime_monitor.py [--api-key API_KEY] [--interval SECONDS] [--max-calls COUNT]

Author: Refactored from monitor_rt_protobuf_flows.py for better functionality and security
"""

import argparse
import sys
import os
import json
import csv
import time
import hashlib
from typing import Optional, List, Dict, Any, Tuple
import logging
from datetime import datetime

import requests
import dataprv_traffic_realtime_data_pb2
from google.protobuf.timestamp_pb2 import Timestamp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RealtimeTrafficMonitor:
    """Monitors real-time traffic data and tracks changes."""
    
    def __init__(self, api_key: str, endpoint: str, output_dir: str = "."):
        self.api_key = api_key
        self.endpoint = endpoint
        self.output_dir = output_dir
        self.previous_data = None
        self.previous_hash = None
        self.previous_snapshot_time = None
        self.difference_info = []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Setup monitoring log file
        self.log_file = os.path.join(output_dir, f"monitor_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        self._init_log_file()
    
    def _init_log_file(self):
        """Initialize the monitoring log CSV file."""
        try:
            with open(self.log_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['timestamp', 'snapshot_time', 'total_records', 'changes_detected', 
                             'new_records', 'updated_records', 'data_hash']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            logger.info(f"Initialized monitoring log: {self.log_file}")
        except Exception as e:
            logger.error(f"Error initializing log file: {e}")
    
    def fetch_data(self) -> Optional[bytes]:
        """Fetch real-time data from the API."""
        headers = {'apiKey': self.api_key}
        
        try:
            response = requests.get(self.endpoint, headers=headers)
            response.raise_for_status()
            return response.content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data: {e}")
            if hasattr(response, 'status_code'):
                if response.status_code == 401:
                    logger.error("Authentication failed. Please check your API key.")
                elif response.status_code == 403:
                    logger.error("Access forbidden. Please check your API key permissions.")
            return None
    
    def parse_data(self, data: bytes) -> Optional[dataprv_traffic_realtime_data_pb2.DataprvTrafficRealtimeDataProto]:
        """Parse protobuf data."""
        try:
            message = dataprv_traffic_realtime_data_pb2.DataprvTrafficRealtimeDataProto()
            message.ParseFromString(data)
            return message
        except Exception as e:
            logger.error(f"Error parsing protobuf data: {e}")
            return None
    
    def extract_traffic_data(self, message) -> Tuple[List[Dict], str]:
        """Extract and normalize traffic data."""
        snapshot_time = message.snapshot_date_time.ToDatetime()
        
        # Sort by olr_code for consistent ordering
        street_traffic_list = sorted(message.street_traffic, key=lambda x: x.olr_code)
        
        # Create normalized data structure
        traffic_data = []
        for street in street_traffic_list:
            street_record = {
                'id': street.id,
                'from_node_id': street.from_node_id,
                'speed_kmh': street.speed_kmh,
                'olr_code': street.olr_code
            }
            
            # Add probe count if available
            if hasattr(street, 'probe_count'):
                street_record['probe_count'] = street.probe_count
                
            traffic_data.append(street_record)
        
        # Create hash for change detection
        data_string = json.dumps(traffic_data, sort_keys=True)
        data_hash = hashlib.sha256(data_string.encode()).hexdigest()[:16]
        
        return traffic_data, data_hash
    
    def detect_changes(self, current_data: List[Dict], current_hash: str) -> Dict[str, Any]:
        """Detect changes between current and previous data."""
        changes = {
            'has_changes': False,
            'new_records': 0,
            'updated_records': 0,
            'total_records': len(current_data)
        }
        
        if self.previous_data is None:
            changes['has_changes'] = True
            changes['new_records'] = len(current_data)
            logger.info("First data collection - all records are new")
        elif current_hash != self.previous_hash:
            changes['has_changes'] = True
            
            # Create lookup dictionaries for comparison
            prev_by_id = {record['id']: record for record in self.previous_data}
            curr_by_id = {record['id']: record for record in current_data}
            
            # Count new records
            new_ids = set(curr_by_id.keys()) - set(prev_by_id.keys())
            changes['new_records'] = len(new_ids)
            
            # Count updated records (same ID but different data)
            for record_id in curr_by_id:
                if record_id in prev_by_id:
                    curr_record = curr_by_id[record_id]
                    prev_record = prev_by_id[record_id]
                    
                    # Compare speed (main changing attribute)
                    if curr_record['speed_kmh'] != prev_record['speed_kmh']:
                        changes['updated_records'] += 1
            
            logger.info(f"Changes detected: {changes['new_records']} new, {changes['updated_records']} updated")
        
        return changes
    
    def log_monitoring_data(self, snapshot_time: datetime, changes: Dict[str, Any], data_hash: str):
        """Log monitoring information to CSV file."""
        try:
            with open(self.log_file, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['timestamp', 'snapshot_time', 'total_records', 'changes_detected', 
                             'new_records', 'updated_records', 'data_hash']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writerow({
                    'timestamp': datetime.now().isoformat(),
                    'snapshot_time': snapshot_time.isoformat() if snapshot_time else None,
                    'total_records': changes['total_records'],
                    'changes_detected': changes['has_changes'],
                    'new_records': changes['new_records'],
                    'updated_records': changes['updated_records'],
                    'data_hash': data_hash
                })
        except Exception as e:
            logger.error(f"Error logging monitoring data: {e}")
    
    def save_snapshot(self, data: List[Dict], snapshot_time: datetime, call_number: int):
        """Save data snapshot when changes are detected."""
        if not data:
            return
            
        timestamp_str = snapshot_time.strftime('%Y%m%d_%H%M%S') if snapshot_time else datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as JSON
        json_path = os.path.join(self.output_dir, f"snapshot_{call_number:04d}_{timestamp_str}.json")
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'snapshot_time': snapshot_time.isoformat() if snapshot_time else None,
                    'call_number': call_number,
                    'record_count': len(data),
                    'traffic_data': data
                }, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved snapshot: {json_path}")
        except Exception as e:
            logger.error(f"Error saving snapshot: {e}")
    
    def monitor(self, max_calls: int = 100, interval: int = 60, save_snapshots: bool = False):
        """Main monitoring loop."""
        logger.info(f"Starting traffic monitoring - Max calls: {max_calls}, Interval: {interval}s")
        logger.info(f"Endpoint: {self.endpoint}")
        logger.info(f"Output directory: {self.output_dir}")
        
        for call_number in range(1, max_calls + 1):
            logger.info(f"Monitoring call {call_number}/{max_calls}")
            
            try:
                # Fetch and parse data
                raw_data = self.fetch_data()
                if raw_data is None:
                    logger.error("Failed to fetch data, skipping this iteration")
                    continue
                
                message = self.parse_data(raw_data)
                if message is None:
                    logger.error("Failed to parse data, skipping this iteration")
                    continue
                
                # Extract traffic data
                current_data, current_hash = self.extract_traffic_data(message)
                snapshot_time = message.snapshot_date_time.ToDatetime() if message.snapshot_date_time else None
                
                # Detect changes
                changes = self.detect_changes(current_data, current_hash)
                
                # Log monitoring information
                self.log_monitoring_data(snapshot_time, changes, current_hash)
                
                # Save snapshot if changes detected and snapshots enabled
                if changes['has_changes'] and save_snapshots:
                    self.save_snapshot(current_data, snapshot_time, call_number)
                
                # Update previous data
                self.previous_data = current_data
                self.previous_hash = current_hash
                self.previous_snapshot_time = snapshot_time
                
                # Display progress
                logger.info(f"Call {call_number}: {changes['total_records']} records, "
                           f"Changes: {'Yes' if changes['has_changes'] else 'No'}")
                
                # Wait for next iteration (except for last call)
                if call_number < max_calls:
                    logger.info(f"Waiting {interval} seconds...")
                    time.sleep(interval)
                    
            except KeyboardInterrupt:
                logger.info("Monitoring interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring iteration {call_number}: {e}")
                continue
        
        # Generate monitoring summary
        self.generate_summary()
        logger.info("Monitoring completed")
    
    def generate_summary(self):
        """Generate monitoring summary report."""
        summary_path = os.path.join(self.output_dir, "monitoring_summary.txt")
        
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("PTV Flows Real-time Traffic Monitoring Summary\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Monitoring started: {datetime.now().isoformat()}\n")
                f.write(f"Endpoint: {self.endpoint}\n")
                f.write(f"Log file: {self.log_file}\n\n")
                
                # Read and analyze log data
                if os.path.exists(self.log_file):
                    try:
                        import pandas as pd
                        df = pd.read_csv(self.log_file)
                        
                        f.write(f"Total monitoring calls: {len(df)}\n")
                        f.write(f"Calls with changes: {df['changes_detected'].sum()}\n")
                        f.write(f"Average records per call: {df['total_records'].mean():.1f}\n")
                        f.write(f"Max records in a call: {df['total_records'].max()}\n")
                        f.write(f"Min records in a call: {df['total_records'].min()}\n")
                        
                    except ImportError:
                        f.write("Pandas not available for detailed statistics\n")
                    except Exception as e:
                        f.write(f"Error analyzing log data: {e}\n")
            
            logger.info(f"Generated monitoring summary: {summary_path}")
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")


def get_monitoring_config() -> Tuple[str, int, int, bool]:
    """Get monitoring configuration from user."""
    print("\n=== Monitoring Configuration ===")
    
    try:
        # API endpoint
        print("Select API environment:")
        print("1. Production: https://api.ptvgroup.tech/flows/realtime-traffic/v1/realtime/traffic")
        print("2. Staging: https://api.ptvgroup.tech/flows/realtime-traffic/v1/realtime/traffic")
        
        while True:
            choice = input("Enter your choice (1 or 2): ").strip()
            if choice == "1":
                endpoint = "https://api.ptvgroup.tech/flows/realtime-traffic/v1/realtime/traffic"
                break
            elif choice == "2":
                endpoint = "https://api.ptvgroup.tech/flows/realtime-traffic/v1/realtime/traffic"
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")
        
        # Monitoring parameters
        max_calls_input = input("Maximum number of calls (default: 100): ").strip()
        max_calls = int(max_calls_input) if max_calls_input else 100
        
        interval_input = input("Interval between calls in seconds (default: 60): ").strip()
        interval = int(interval_input) if interval_input else 60
        
        snapshots_input = input("Save data snapshots when changes detected? (y/N): ").strip().lower()
        save_snapshots = snapshots_input == 'y'
        
        return endpoint, max_calls, interval, save_snapshots
        
    except (ValueError, KeyboardInterrupt) as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Monitor PTV Flows real-time traffic data for changes')
    parser.add_argument('--api-key', type=str,
                       help='PTV API key (if not provided, will use default placeholder)')
    parser.add_argument('--endpoint', type=str,
                       help='API endpoint URL (if not provided, will prompt user)')
    parser.add_argument('--output-dir', type=str, default='./monitoring_output',
                       help='Output directory for monitoring files (default: ./monitoring_output)')
    parser.add_argument('--max-calls', type=int, default=100,
                       help='Maximum number of API calls (default: 100)')
    parser.add_argument('--interval', type=int, default=60,
                       help='Interval between calls in seconds (default: 60)')
    parser.add_argument('--save-snapshots', action='store_true',
                       help='Save data snapshots when changes are detected')
    parser.add_argument('--no-interactive', action='store_true',
                       help='Skip interactive configuration prompts')
    
    args = parser.parse_args()
    
    # Handle API key
    default_api_key = "change_me_to_your_api_key"
    api_key = args.api_key or default_api_key
    
    if api_key == default_api_key:
        logger.warning("Using default placeholder API key. Please provide your actual API key using --api-key")
        logger.warning("Get your API key from: https://ptvgroup.tech/flows/")
    
    # Get configuration
    if args.no_interactive:
        endpoint = args.endpoint or "https://api.ptvgroup.tech/flows/realtime-traffic/v1/realtime/traffic"
        max_calls = args.max_calls
        interval = args.interval
        save_snapshots = args.save_snapshots
    else:
        endpoint, max_calls, interval, save_snapshots = get_monitoring_config()
        # Override with command line arguments if provided
        if args.endpoint:
            endpoint = args.endpoint
        if args.max_calls != 100:
            max_calls = args.max_calls
        if args.interval != 60:
            interval = args.interval
        if args.save_snapshots:
            save_snapshots = True
    
    try:
        # Initialize monitor
        monitor = RealtimeTrafficMonitor(api_key, endpoint, args.output_dir)
        
        # Start monitoring
        monitor.monitor(max_calls, interval, save_snapshots)
        
    except KeyboardInterrupt:
        logger.info("Monitoring cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()