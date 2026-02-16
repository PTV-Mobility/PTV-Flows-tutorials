#!/usr/bin/env python3
"""
Example usage of PTV Flows Network Downloader
Downloads network data for a small area in Rome and saves to CSV and TopoJSON
"""

import subprocess
import sys
import os

def run_example():
    """Run an example download for Rome area"""
    
    print("PTV Flows Network Downloader - Example")
    print("======================================")
    print()
    print("This example will download network data for a small area in Rome")
    print("and save it to both CSV and TopoJSON formats.")
    print()
    
    # Rome coordinates (small area around EUR - Roma)
    
    rome_coords = "12.442961, 41.817077, 12.491369, 41.845216"
    
    print(f"Using coordinates: {rome_coords}")
    print("(Small area in Rome around the historical center)")
    print()
    
    # Create output directory
    output_dir = "example_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Run the downloader
    cmd = [
        sys.executable, 
        "ptv_flows_downloader.py",
        "--output-dir", output_dir
    ]
    
    try:
        print("Running PTV Flows downloader...")
        print("When prompted, enter the coordinates above or press Enter to use them automatically.")
        print()
        
        # Run with the coordinates as input
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=rome_coords + "\n")
        
        print("--- Output ---")
        if stdout:
            print(stdout)
        if stderr:
            print(stderr)
        
        if process.returncode == 0:
            print("✅ Example completed successfully!")
            print(f"Check the '{output_dir}' directory for the generated files.")
            
            # List output files
            if os.path.exists(output_dir):
                files = os.listdir(output_dir)
                if files:
                    print("\nGenerated files:")
                    for file in files:
                        file_path = os.path.join(output_dir, file)
                        size = os.path.getsize(file_path)
                        print(f"  {file} ({size:,} bytes)")
        else:
            print("❌ Example failed. Check the output above for errors.")
            return False
            
    except Exception as e:
        print(f"❌ Error running example: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_example()
    sys.exit(0 if success else 1)