#!/usr/bin/env python3
"""
Setup script for PTV Flows Realtime API Client
Installs dependencies and sets up the environment
"""

import subprocess
import sys
import os

def main():
    """Setup the PTV Flows Realtime API Client environment"""
    
    print("PTV Flows Realtime API Client - Setup")
    print("======================================")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        print("⚠️  WARNING: You are not in a virtual environment!")
        print("   It's recommended to create a virtual environment first:")
        print("   python -m venv venv")
        print("   .\\venv\\Scripts\\activate  (Windows)")
        print("   source venv/bin/activate  (Linux/Mac)")
        print()
        
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return False
    
    # Install requirements
    print("Installing Python packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    
    # Check if protobuf files exist
    required_files = [
        "dataprv_traffic_realtime_data_pb2.py",
        "dataprv_traffic_realtime_data.proto"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("⚠️  Missing protobuf files:")
        for file in missing_files:
            print(f"   - {file}")
        print("   These files are required for the scripts to work properly.")
    else:
        print("✅ All required protobuf files found!")
    
    print()
    print("✅ Setup completed successfully!")
    print()
    print("To use the PTV Flows Realtime API Client:")
    print("  Single data fetch:")
    print("    python ptv_flows_realtime.py --api-key YOUR_API_KEY")
    print()
    print("  Continuous monitoring:")
    print("    python ptv_flows_realtime_monitor.py --api-key YOUR_API_KEY")
    print()
    print("For help:")
    print("  python ptv_flows_realtime.py --help")
    print("  python ptv_flows_realtime_monitor.py --help")
    print()
    print("🔑 Get your API key from: https://ptvgroup.tech/flows/")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)