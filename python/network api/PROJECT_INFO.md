# PTV Flows Network API Tutorial

**Location**: `C:\Users\luca.paone\GitHub\PTV-Mobility\PTV-Flows-tutorials\python\network api`

## Project Structure

```
network api/
├── ptv_flows_downloader.py    # Main script
├── flows_network_v1_pb2.py    # Protobuf definitions
├── requirements.txt           # Python dependencies
├── setup.py                   # Installation script
├── example.py                 # Example usage
├── README.md                  # Documentation
└── PROJECT_INFO.md           # This file
```

## Files Description

- **ptv_flows_downloader.py**: Main script that downloads PTV Flows network data, filters by bounding box, and exports to CSV/TopoJSON
- **flows_network_v1_pb2.py**: Protocol Buffer definitions for PTV Flows data structures (generated from .proto file)
- **requirements.txt**: Minimal set of Python dependencies required for this project
- **setup.py**: Automated setup script that creates virtual environment and installs dependencies
- **example.py**: Example script that demonstrates usage with Rome coordinates
- **README.md**: Complete documentation with usage instructions and examples

## Dependencies

Core dependencies (automatically installed by setup.py):
- pandas, numpy: Data processing
- geopandas, shapely: Geographic data handling
- requests: HTTP API calls
- protobuf: Protocol Buffer deserialization
- topojson: TopoJSON format export

## API Details

- **Endpoint**: `https://api.ptvgroup.tech/flows/map/v1/streets`
- **Authentication**: API key required
- **Format**: Protocol Buffer (gzip compressed)
- **Data**: Street network with geometry and attributes

## Created On

September 19, 2025 - Extracted from PTV-Flows-Net-Matching project