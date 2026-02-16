#!/usr/bin/env python3
"""
Setup script for PTV Flows Historical Data API (HDA) tutorial

This script automates the setup process for the HDA API tutorial environment.
It installs required dependencies and verifies the installation.

Usage:
    python setup.py

Author: PTV Flows Tutorial
Date: October 28, 2025
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header():
    """Print setup header information."""
    print("PTV Flows Historical Data API (HDA) - Setup")
    print("=" * 50)
    print("This setup script will:")
    print("• Install required Python packages")
    print("• Verify dependencies are working")
    print("• Create output directories")
    print("• Test basic functionality")
    print()

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print("   This tutorial requires Python 3.7 or higher")
        print("   Please upgrade your Python installation")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def install_requirements():
    """Install required packages from requirements.txt."""
    print("\n📦 Installing required packages...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        # Upgrade pip first
        print("   Upgrading pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                            stdout=subprocess.DEVNULL)
        
        # Install requirements
        print("   Installing packages from requirements.txt...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Package installation failed")
            print(f"Error: {result.stderr}")
            return False
        
        print("✅ All packages installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during installation: {e}")
        return False

def verify_dependencies():
    """Verify that all required dependencies are importable."""
    print("\n🔍 Verifying dependencies...")
    
    required_packages = [
        ("requests", "HTTP client library"),
        ("pandas", "Data analysis library"),
        ("numpy", "Numerical computing"),
        ("pyarrow", "Parquet file support"),
        ("dateutil", "Date/time utilities")
    ]
    
    optional_packages = [
        ("geopandas", "Geospatial analysis"),
        ("matplotlib", "Plotting library"),
        ("plotly", "Interactive visualizations"),
        ("folium", "Map visualization"),
        ("tqdm", "Progress bars")
    ]
    
    all_good = True
    
    # Check required packages
    print("   Required packages:")
    for package_name, description in required_packages:
        try:
            if package_name == "dateutil":
                import dateutil
            else:
                __import__(package_name)
            print(f"   ✅ {package_name} - {description}")
        except ImportError:
            print(f"   ❌ {package_name} - {description} (MISSING)")
            all_good = False
    
    # Check optional packages
    print("   Optional packages:")
    optional_missing = []
    for package_name, description in optional_packages:
        try:
            __import__(package_name)
            print(f"   ✅ {package_name} - {description}")
        except ImportError:
            print(f"   ⚠️  {package_name} - {description} (optional, not installed)")
            optional_missing.append(package_name)
    
    if optional_missing:
        print(f"\n   ℹ️  {len(optional_missing)} optional packages not installed.")
        print("   You can install them later if needed for advanced features.")
    
    return all_good

def create_directories():
    """Create necessary output directories."""
    print("\n📁 Creating directories...")
    
    directories = [
        "output",
        "config", 
        "scripts",
        "tests"
    ]
    
    created = []
    for directory in directories:
        dir_path = Path(__file__).parent / directory
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                created.append(directory)
            except Exception as e:
                print(f"   ❌ Failed to create {directory}: {e}")
                return False
    
    if created:
        print(f"   ✅ Created directories: {', '.join(created)}")
    else:
        print("   ✅ All directories already exist")
    
    return True

def test_hda_client():
    """Test basic HDA client functionality."""
    print("\n🔧 Testing HDA client...")
    
    try:
        # Import the client
        from ptv_flows_hda_client import create_hda_client, HdaApiError
        print("   ✅ HDA client imported successfully")
        
        # Create client with dummy API key (won't make actual requests)
        client = create_hda_client(api_key="test_key", debug=False)
        print("   ✅ HDA client created successfully")
        
        # Check available formats
        formats = client.get_available_formats()
        print(f"   ✅ Available formats: {', '.join(formats)}")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Failed to import HDA client: {e}")
        return False
    except Exception as e:
        print(f"   ❌ HDA client test failed: {e}")
        return False

def print_next_steps():
    """Print information about next steps."""
    print("\n🎯 Setup Complete! Next Steps:")
    print("-" * 30)
    print()
    print("1. 🔑 Get your API key:")
    print("   Visit: https://ptvgroup.tech/flows/")
    print()
    print("2. 🚀 Run the example:")
    print("   python example.py")
    print()
    print("3. 📚 Read the documentation:")
    print("   Open README.md for detailed usage instructions")
    print()
    print("4. ⚙️  Set environment variable (optional):")
    print("   export PTV_API_KEY=\"your_api_key_here\"")
    print()
    print("5. 🔍 Explore advanced features:")
    print("   Check the scripts/ directory for specialized tools")
    print()

def main():
    """Main setup function."""
    print_header()
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed during package installation")
        return False
    
    # Verify dependencies
    if not verify_dependencies():
        print("\n❌ Setup failed during dependency verification")
        print("   Some required packages are missing")
        return False
    
    # Create directories
    if not create_directories():
        print("\n❌ Setup failed during directory creation")
        return False
    
    # Test HDA client
    if not test_hda_client():
        print("\n❌ Setup failed during HDA client testing")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during setup: {e}")
        sys.exit(1)