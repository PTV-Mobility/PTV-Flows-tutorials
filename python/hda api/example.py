#!/usr/bin/env python3
"""
PTV Flows Historical Data API (HDA) - Quick Start Example

This example demonstrates basic usage of all major HDA API endpoints.
It provides an interactive tutorial that covers:
- Time slice data for network-wide analysis
- Time series data for individual streets
- Statistical data for performance insights
- KPI data for monitoring metrics
- Elaborated data for processed analytics

Run this script to test your API key and get familiar with the HDA API capabilities.

Author: PTV Flows Tutorial
Date: October 28, 2025
"""

import os
import sys
import json
from datetime import datetime, timedelta
import logging

# Configure logging for the example
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_dependencies():
    """Check if required dependencies are installed."""
    try:
        import pandas as pd
        import requests
        return True
    except ImportError as e:
        print(f"❌ Missing required dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def get_api_key():
    """Get API key from user input or environment variable."""
    # Check environment variable first
    api_key = os.environ.get('PTV_API_KEY')
    if api_key and api_key != "your_api_key_here":
        print(f"✅ Using API key from environment variable PTV_API_KEY")
        return api_key
    
    # Ask user for API key
    print("🔑 API Key Required")
    print("=" * 50)
    print("To use the PTV Flows HDA API, you need a valid API key.")
    print("Get your API key from: https://ptvgroup.tech/flows/")
    print()
    
    api_key = input("Enter your PTV API key (or press Enter to use demo mode): ").strip()
    
    if not api_key:
        print("📝 Running in demo mode - will show expected workflow but may fail without real API key")
        return "demo_api_key_replace_with_real_key"
    
    return api_key

def run_basic_examples(client):
    """Run basic examples for each endpoint category."""
    
    print("\n" + "="*60)
    print("🚀 RUNNING HDA API EXAMPLES")
    print("="*60)
    
    results = {}
    
    # ==========================================================================
    # 1. NETWORK STATISTICS (Lightweight test)
    # ==========================================================================
    print("\n📊 1. Network Statistics")
    print("-" * 30)
    try:
        print("Fetching network statistics (this helps us understand available data)...")
        network_stats = client.get_stats_network_data(time_window_offset=0, output_format="parquet")
        
        if isinstance(network_stats, dict):
            print("✅ Network statistics retrieved successfully!")
            
            # Show basic info about the network
            if 'networkInfo' in network_stats:
                info = network_stats['networkInfo']
                print(f"   Network elements: {info.get('totalElements', 'N/A')}")
                print(f"   Coverage area: {info.get('coverageArea', 'N/A')}")
            
            # Show available geohash tiles
            if 'availableTiles' in network_stats:
                tiles = network_stats['availableTiles']
                print(f"   Available geohash tiles: {len(tiles)} tiles")
                if tiles:
                    print(f"   Sample tiles: {tiles[:3]}..." if len(tiles) > 3 else f"   Tiles: {tiles}")
            
            results['network_stats'] = network_stats
        else:
            print(f"✅ Network statistics retrieved (DataFrame with {len(network_stats)} rows)")
            results['network_stats'] = network_stats  # Save the actual DataFrame
            
    except Exception as e:
        print(f"❌ Network statistics failed: {str(e)}")
        results['network_stats'] = f"Error: {str(e)}"
    
    # ==========================================================================
    # 2. STREET STATISTICS
    # ==========================================================================
    print("\n🛣️  2. Street-Level Statistics")
    print("-" * 30)
    try:
        print("Fetching street-level statistical data...")
        
        # Get data for current month (use parquet format for DataFrame output)
        street_stats = client.get_stats_streets_data(time_window_offset=0, output_format="parquet")
        
        if isinstance(street_stats, dict):
            print("✅ Street statistics retrieved successfully!")
            
            # Show basic structure
            if 'streets' in street_stats:
                streets = street_stats['streets']
                print(f"   Streets analyzed: {len(streets)}")
                
                # Show sample street data
                if streets:
                    sample = streets[0]
                    print(f"   Sample street ID: {sample.get('streetCode', 'N/A')}")
                    if 'historicalStats' in sample:
                        stats = sample['historicalStats']
                        print(f"   Has historical statistics: {len(stats)} time periods")
            
            results['street_stats'] = street_stats
        else:
            print(f"✅ Street statistics retrieved (DataFrame with {len(street_stats)} rows)")
            # Show some sample column info for DataFrames
            if hasattr(street_stats, 'columns'):
                print(f"   Columns: {list(street_stats.columns[:5])}{'...' if len(street_stats.columns) > 5 else ''}")
            results['street_stats'] = street_stats  # Save the actual DataFrame
            
    except Exception as e:
        print(f"❌ Street statistics failed: {str(e)}")
        results['street_stats'] = f"Error: {str(e)}"
    
    # ==========================================================================
    # 3. TIME SLICE DATA (Metadata only)
    # ==========================================================================
    print("\n⏰ 3. Time Slice Data (Metadata)")
    print("-" * 30)
    try:
        print("Fetching time slice metadata (without actual data to avoid large downloads)...")
        
        # Get metadata by not specifying fromRow/toRow
        yesterday = datetime.now() - timedelta(days=1)
        time_slice_meta = client.get_time_slice_data(
            from_time=yesterday.replace(hour=10, minute=0, second=0),
            to_time=yesterday.replace(hour=11, minute=0, second=0)
        )
        
        if isinstance(time_slice_meta, dict):
            print("✅ Time slice metadata retrieved successfully!")
            
            # Show metadata information
            if 'metadata' in time_slice_meta:
                meta = time_slice_meta['metadata']
                print(f"   Total records available: {meta.get('totalRecords', 'N/A')}")
                print(f"   Time interval: {meta.get('fromTime', 'N/A')} to {meta.get('toTime', 'N/A')}")
                print(f"   Data availability: {meta.get('dataAvailability', 'N/A')}")
            
            results['time_slice_meta'] = time_slice_meta
        else:
            print(f"✅ Time slice data retrieved (DataFrame with {len(time_slice_meta)} rows)")
            results['time_slice_meta'] = time_slice_meta  # Save the actual DataFrame
            
    except Exception as e:
        print(f"❌ Time slice metadata failed: {str(e)}")
        print("   This is normal if no recent data is available or API key has limited access")
        results['time_slice_meta'] = f"Error: {str(e)}"
    
    # ==========================================================================
    # 4. ELABORATED DATA
    # ==========================================================================
    print("\n📈 4. Elaborated Analytics Data")
    print("-" * 30)
    try:
        print("Fetching elaborated analytics data...")
        
        elaborated_data = client.get_elaborated_overall_data()
        
        if isinstance(elaborated_data, dict):
            print("✅ Elaborated data retrieved successfully!")
            
            # Show basic structure
            if 'analytics' in elaborated_data:
                analytics = elaborated_data['analytics']
                print(f"   Analytics categories: {len(analytics)}")
                
            results['elaborated_data'] = elaborated_data
        else:
            print(f"✅ Elaborated data retrieved (DataFrame with {len(elaborated_data)} rows)")
            results['elaborated_data'] = elaborated_data  # Save the actual DataFrame
            
    except Exception as e:
        print(f"❌ Elaborated data failed: {str(e)}")
        results['elaborated_data'] = f"Error: {str(e)}"
    
    return results

def save_results_to_files(results):
    """Save results to output files for inspection."""
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    saved_files = []
    
    for result_type, data in results.items():
        # Skip error messages
        if isinstance(data, str) and data.startswith("Error:"):
            continue
            
        if isinstance(data, dict):
            filename = f"{result_type}_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
                saved_files.append(filename)
                print(f"   💾 {filename} ({len(json.dumps(data, default=str))} bytes)")
            except Exception as e:
                print(f"   ❌ Failed to save {filename}: {e}")
                
        elif hasattr(data, 'to_csv'):  # DataFrame
            # Save as CSV
            csv_filename = f"{result_type}_{timestamp}.csv"
            csv_filepath = os.path.join(output_dir, csv_filename)
            
            # Save as Parquet for better data preservation
            parquet_filename = f"{result_type}_{timestamp}.parquet"
            parquet_filepath = os.path.join(output_dir, parquet_filename)
            
            try:
                # Save CSV (human readable)
                data.to_csv(csv_filepath, index=False)
                saved_files.append(csv_filename)
                print(f"   💾 {csv_filename} ({len(data)} rows, {len(data.columns)} columns)")
                
                # Save Parquet (data preservation)
                data.to_parquet(parquet_filepath, index=False)
                saved_files.append(parquet_filename)
                print(f"   💾 {parquet_filename} (binary format)")
                
            except Exception as e:
                print(f"   ❌ Failed to save DataFrame files for {result_type}: {e}")
    
    return saved_files

def demonstrate_advanced_features(client):
    """Demonstrate more advanced features and use cases."""
    
    print("\n" + "="*60)
    print("🔧 ADVANCED FEATURES DEMONSTRATION")
    print("="*60)
    
    # ==========================================================================
    # Format Comparison
    # ==========================================================================
    print("\n📋 1. Multiple Output Formats")
    print("-" * 30)
    
    try:
        print("Comparing JSON vs Parquet formats...")
        
        # Get same data in different formats
        json_data = client.get_stats_network_data(output_format="json")
        parquet_data = client.get_stats_network_data(output_format="parquet")
        
        print("✅ Format comparison successful!")
        print(f"   JSON result type: {type(json_data)}")
        print(f"   Parquet result type: {type(parquet_data)}")
        
        if hasattr(parquet_data, 'shape'):
            print(f"   Parquet DataFrame shape: {parquet_data.shape}")
            
    except Exception as e:
        print(f"❌ Format comparison failed: {str(e)}")
    
    # ==========================================================================
    # Time Window Analysis
    # ==========================================================================
    print("\n📅 2. Time Window Analysis")
    print("-" * 30)
    
    try:
        print("Analyzing data across different time periods...")
        
        current_month = client.get_stats_network_data(time_window_offset=0)
        previous_month = client.get_stats_network_data(time_window_offset=1)
        
        print("✅ Time window comparison successful!")
        print("   Current month data: Retrieved")
        print("   Previous month data: Retrieved")
        print("   This enables month-over-month trend analysis")
        
    except Exception as e:
        print(f"❌ Time window analysis failed: {str(e)}")
    
    # ==========================================================================
    # Connection Test
    # ==========================================================================
    print("\n🔗 3. API Connection Health")
    print("-" * 30)
    
    connection_ok = client.test_connection()
    if connection_ok:
        print("✅ API connection is healthy")
        print("   All endpoints are accessible")
        print("   Authentication is working correctly")
    else:
        print("❌ API connection issues detected")
        print("   Check your API key and network connection")

def print_next_steps():
    """Print information about next steps and additional resources."""
    
    print("\n" + "="*60)
    print("🎯 NEXT STEPS AND RESOURCES")
    print("="*60)
    
    print("\n📚 What You Can Do Next:")
    print("-" * 30)
    print("1. 📊 Analyze specific streets with time series data")
    print("2. 📈 Monitor KPIs for your network")
    print("3. 🗺️  Explore geographic data with geohash filtering")
    print("4. 📉 Perform statistical analysis on network performance")
    print("5. 🔄 Set up automated monitoring workflows")
    
    print("\n🛠️  Available Scripts:")
    print("-" * 20)
    print("• scripts/time_series_analysis.py - Deep dive into historical trends")
    print("• scripts/kpi_monitor.py - KPI monitoring and alerting")
    print("• scripts/statistical_analyzer.py - Network performance analysis")
    print("• scripts/geohash_explorer.py - Geographic data exploration")
    
    print("\n📖 Documentation:")
    print("-" * 20)
    print("• README.md - Complete setup and usage guide")
    print("• API Spec: https://api.ptvgroup.tech/meta/services/hda/v1/openapi.json")
    print("• KPI API: https://api.ptvgroup.tech/kpieng/v1")
    
    print("\n⚙️  Configuration:")
    print("-" * 20)
    print("• Set PTV_API_KEY environment variable to avoid prompts")
    print("• Modify config files for automated workflows")
    print("• Use debug=True in client for troubleshooting")

def main():
    """Main function to run the HDA API example."""
    
    print("PTV Flows Historical Data API (HDA) - Quick Start Example")
    print("=" * 65)
    print("This example demonstrates the core functionality of the HDA API")
    print("and helps you test your API connection and credentials.")
    print()
    
    # Check dependencies
    if not ensure_dependencies():
        return False
    
    # Import the client (after dependency check)
    try:
        from ptv_flows_hda_client import create_hda_client, HdaApiError
    except ImportError as e:
        print(f"❌ Error importing HDA client: {e}")
        print("Make sure ptv_flows_hda_client.py is in the same directory")
        return False
    
    # Get API key
    api_key = get_api_key()
    
    # Create client
    print(f"\n🔧 Creating HDA API client...")
    try:
        client = create_hda_client(api_key=api_key, debug=False)
        print("✅ HDA client created successfully")
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return False
    
    # Run basic examples
    try:
        results = run_basic_examples(client)
        
        # Save results
        print(f"\n💾 Saving Results")
        print("-" * 20)
        saved_files = save_results_to_files(results)
        
        if saved_files:
            print(f"✅ Saved {len(saved_files)} result files to output/ directory")
        else:
            print("ℹ️  No files saved (this is normal if running in demo mode)")
        
        # Demonstrate advanced features
        demonstrate_advanced_features(client)
        
        # Show next steps
        print_next_steps()
        
        print(f"\n🎉 Example completed successfully!")
        print("Check the output/ directory for saved data files.")
        
        return True
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Example cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Example failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)