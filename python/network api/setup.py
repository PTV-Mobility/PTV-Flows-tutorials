#!/usr/bin/env python3
"""
Setup script for PTV Flows Network Downloader
Installs dependencies and sets up the environment
"""

import subprocess
import sys
import os

def main():
    """Setup the PTV Flows Network Downloader environment"""
    
    print("PTV Flows Network Downloader - Setup")
    print("=====================================")
    
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
    
    # Check if flows_network_v1_pb2.py exists
    if not os.path.exists("flows_network_v1_pb2.py"):
        print("❌ Error: flows_network_v1_pb2.py not found!")
        print("   This file is required for the script to work.")
        print("   Make sure it's in the same directory as the script.")
        return False
    
    print()
    print("✅ Setup completed successfully!")
    print()
    print("To use the PTV Flows Network Downloader:")
    print("  python ptv_flows_downloader.py")
    print()
    print("For help:")
    print("  python ptv_flows_downloader.py --help")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)