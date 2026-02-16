# PTV Flows Network API - Python Tutorial

This tutorial demonstrates how to download network data from the PTV Flows API, filter it by geographic bounding box, and export it in multiple formats (CSV and TopoJSON).

## Quick Start

1. **Setup Environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   python setup.py
   ```

2. **Run Example**:
   ```bash
   python example.py
   ```

3. **Custom Usage**:
   ```bash
   python ptv_flows_downloader.py
   ```

## Features

- Downloads street network data from PTV Flows API
- Interactive bounding box input with validation
- Spatial filtering by bounding box intersection
- Exports data in CSV and TopoJSON formats
-- Support for production API endpoint
- Comprehensive error handling and logging

## Prerequisites

1. **Python Dependencies**: Install the required packages using:
   ```bash
   pip install -r requirements.txt
   ```

2. **FMM Library**: Make sure you have the `flows_network_v1_pb2.py` file in the same directory as the script. This is the protobuf-generated Python module for PTV Flows data structures.

3. **PTV API Key**: You'll need a valid PTV API key. The script includes a default key, but you can provide your own using the `--api-key` argument.

## Installation

1. Clone or download the project files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure `flows_network_v1_pb2.py` is in the same directory
4. Run the script:
   ```bash
   python ptv_flows_downloader.py
   ```

## Usage

### Basic Usage
```bash
python ptv_flows_downloader.py
```

### With Custom API Key
```bash
python ptv_flows_downloader.py --api-key YOUR_API_KEY
```

### Using Staging Environment
```bash
python ptv_flows_downloader.py --staging
```

### Custom Output Directory
```bash
python ptv_flows_downloader.py --output-dir ./output
```

### Debug Mode (saves raw downloaded data)
```bash
python ptv_flows_downloader.py --debug
```

## Interactive Input

When you run the script, it will prompt you to enter bounding box coordinates:

```
Please enter the bounding box coordinates:
Format: minimum longitude, minimum latitude, maximum longitude, maximum latitude
Example: 2.3, 48.8, 2.4, 48.9 (for central Paris)
Enter coordinates (min_lon, min_lat, max_lon, max_lat): 
```

### Example Bounding Boxes

- **Central Paris**: `2.3, 48.8, 2.4, 48.9`
- **Manhattan**: `-74.0, 40.7, -73.9, 40.8`
- **Central London**: `-0.2, 51.4, -0.1, 51.6`
- **Rome Center**: `12.4, 41.8, 12.6, 42.0`

## Output Files

The script generates two files with names based on your bounding box coordinates:

1. **CSV File**: `ptv_flows_network_{min_lon}_{min_lat}_{max_lon}_{max_lat}.csv`
   - Contains tabular data with street attributes
   - Geometry stored as WKT (Well-Known Text) in `shape_wkt` column

2. **TopoJSON File**: `ptv_flows_network_{min_lon}_{min_lat}_{max_lon}_{max_lat}.topojson`
   - Geographic format suitable for web mapping
   - Falls back to GeoJSON if topojson library is not available

## Data Structure

The exported data includes the following fields:

- `id`: Street identifier
- `from_node_id`: Starting node identifier  
- `openlr`: OpenLR encoding (hex string)
- `functional_road_class`: Road classification
- `form_of_way`: Road type (highway, arterial, etc.)
- `free_flow_speed_kmph`: Speed limit in km/h
- `shape_wkt`: Geometry as Well-Known Text (CSV only)
- `name`: Street name (if available)
- `geometry`: Shapely geometry object (GeoDataFrame only)

## Environment Setup

If you need to set up the complete environment including the FMM library, refer to the `script to create enviroment for map matching flows.bash` file for the full setup procedure.

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all required packages are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. **Missing protobuf module**: Ensure `flows_network_v1_pb2.py` is in the same directory as the script.

3. **API Key Issues**: 
   - Check that your API key is valid
   - Use `--staging` flag if testing with staging credentials

4. **Empty Results**: 
   - Verify your bounding box coordinates are correct
   - Try a larger bounding box area
   - Check that the API is returning data for your region

5. **TopoJSON Issues**: If TopoJSON export fails, the script will save as GeoJSON instead.

## Related Files

- `FlowsNetMatching-v6.ipynb`: Original notebook with map matching functionality
- `flows_network_v1_pb2.py`: Protocol buffer definitions for PTV Flows data
- `requirements.txt`: Python package dependencies
- `script to create enviroment for map matching flows.bash`: Full environment setup script

## Utilities

### Flatten parquet to CSV/Parquet

There is a helper script that reads the example parquet produced in `example_output/`,
explodes the nested `values` column and writes a flattened parquet and CSV file:

- Script: `scripts/deserialize_parquet.py`
- Input: the first `.parquet` file found in `example_output/`
- Outputs written to `example_output/`:
   - `flattened.parquet` — flattened parquet file
   - `flattened.csv` — flattened CSV with datetimes as ISO strings

Example (recommended: use the included virtual environment):

```powershell
# run without activating the venv interactively by calling the venv python directly
& ".\.venv\Scripts\python.exe" scripts\deserialize_parquet.py
```

After running you will find `example_output/flattened.csv` and `example_output/flattened.parquet`.


## License

This project is licensed under the MIT License. See the  LICENSE at https://github.com/PTV-Mobility/PTV-Flows-tutorials/blob/19da1c7a603f988ffd806fa0425dd7ae9902ab08/LICENSE  for details.
