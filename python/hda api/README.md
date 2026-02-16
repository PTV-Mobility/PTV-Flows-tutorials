# PTV Flows Historical Data API (HDA) - Python Tutorial

This tutorial demonstrates how to use the PTV Flows Historical Data API to access and analyze traffic data across different time periods. The HDA API provides comprehensive historical traffic information including time series data, statistical analysis, KPI monitoring, and elaborated analytics.

## 🚀 Quick Start

1. **Setup Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate.bat  # Windows
   pip install -r requirements.txt
   ```

2. **Set API Key** (optional but recommended):
   ```bash
   export PTV_API_KEY="your_api_key_here"  # Linux/Mac
   # or
   set PTV_API_KEY=your_api_key_here       # Windows
   ```

3. **Run Quick Example**:
   ```bash
   python example.py
   ```

## ✨ Features

- **Complete API Coverage** - All 9 HDA API endpoints implemented
- **Multiple Output Formats** - JSON, Parquet, and CSV support
- **Interactive Examples** - Guided tutorials for each endpoint type
- **Error Handling** - Comprehensive error handling with helpful messages
- **Data Processing** - Built-in pandas integration for analysis
- **Flexible Authentication** - API key via parameter, environment, or prompt
- **Debug Mode** - Detailed logging for troubleshooting
- **Output Management** - Automatic file saving with timestamps

## 📊 API Endpoints Covered

### 1. Time Slice Data
- **`/time-slice/get`** - Download speed data for entire network within time intervals
- Use case: Bulk network analysis, incident detection, performance monitoring

### 2. Time Series Data  
- **`/time-series/get`** - Historical trends for individual street segments
- Use case: Street-level analysis, seasonal patterns, travel time analysis

### 3. Statistical Network Data
- **`/stats/streets/get`** - Street-level statistical distributions
- **`/stats/freeflow/get`** - Free-flow speed statistical analysis  
- **`/stats/network/get`** - Network-wide statistics and geohash tiles
- Use case: Performance benchmarking, network optimization, capacity planning

### 4. KPI Data
- **`/kpi/overall/get`** - Overall key performance indicators
- **`/kpi/detailed/get`** - Detailed KPI analysis and breakdowns
- Use case: Performance monitoring, SLA tracking, executive reporting

### 5. Elaborated Data
- **`/elaborated/byHoursAndDays/get`** - Processed analytics by time patterns
- **`/elaborated/overall/get`** - Overall processed analytics
- Use case: Advanced analytics, pattern recognition, business intelligence

## 🛠️ Installation

### Prerequisites

- **Python 3.7+** installed on your system
- **PTV API Key** - Get yours at [https://ptvgroup.tech/flows/](https://ptvgroup.tech/flows/)
- **Internet connection** for API requests

### Setup Steps

1. **Clone or Download** the tutorial files to your local machine

2. **Create Virtual Environment** (recommended):
   ```bash
   cd "python/hda api"
   python -m venv venv
   ```

3. **Activate Virtual Environment**:
   ```bash
   # Linux/Mac
   source venv/bin/activate
   
   # Windows Command Prompt
   venv\Scripts\activate.bat
   
   # Windows PowerShell
   venv\Scripts\Activate.ps1
   ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Verify Installation**:
   ```bash
   python -c "import pandas, requests, pyarrow; print('✅ All dependencies installed')"
   ```

## 📖 Usage Examples

### Basic Client Usage

```python
from ptv_flows_hda_client import create_hda_client
from datetime import datetime, timedelta

# Create client
client = create_hda_client(api_key="your_api_key_here")

# Test connection
if client.test_connection():
    print("✅ Connected to HDA API")
```

### Time Series Analysis

```python
# Get hourly speed data for a street
yesterday = datetime.now() - timedelta(days=1)
week_ago = yesterday - timedelta(days=7)

data = client.get_time_series_data(
    street_code="ABC123",
    from_time=week_ago,
    to_time=yesterday,
    time_aggregation="HOURS_1",
    value_type="speed",
    output_format="parquet"  # Returns pandas DataFrame
)

print(f"Retrieved {len(data)} hourly records")
print(f"Average speed: {data['speed'].mean():.1f} km/h")
```

### Network Statistics

```python
# Get network-wide statistics
network_stats = client.get_stats_network_data(time_window_offset=0)

# Get street-level statistics
street_stats = client.get_stats_streets_data(
    time_window_offset=0,
    selected_tile="u0vjn"  # Geohash tile
)
```

### Bulk Data Download

```python
# Download time slice data
from_time = "2024-10-21T10:00:00Z"
to_time = "2024-10-21T11:00:00Z"

# Get metadata first
metadata = client.get_time_slice_data(from_time, to_time)
print(f"Available records: {metadata['metadata']['totalRecords']}")

# Download specific range
data = client.get_time_slice_data(
    from_time, to_time,
    from_row=1, to_row=1000,
    output_format="parquet"
)
```

## 📁 File Structure

```
python/hda api/
├── README.md                    # This documentation
├── requirements.txt             # Python dependencies
├── ptv_flows_hda_client.py     # Main HDA API client
├── example.py                   # Quick start tutorial
├── setup.py                    # Environment setup (coming soon)
├── output/                     # Generated output files
├── scripts/                    # Advanced analysis tools (coming soon)
├── config/                     # Configuration files (coming soon)
└── tests/                      # Test suite (coming soon)
```

## 🔧 Configuration

### API Key Management

The client supports multiple ways to provide your API key:

1. **Environment Variable** (recommended):
   ```bash
   export PTV_API_KEY="your_api_key_here"
   ```

2. **Direct Parameter**:
   ```python
   client = create_hda_client(api_key="your_api_key_here")
   ```

3. **Interactive Prompt**: The example script will prompt for the key if not found

### Output Formats

All endpoints support multiple output formats:

- **`"json"`** - Standard JSON format (dict)
- **`"parquet"`** - Binary format, returns pandas DataFrame
- **`"csv"`** - Compressed CSV format, returns pandas DataFrame

```python
# Get data in different formats
json_data = client.get_stats_network_data(output_format="json")
df_data = client.get_stats_network_data(output_format="parquet")
csv_data = client.get_stats_network_data(output_format="csv")
```

### Debug Mode

Enable detailed logging for troubleshooting:

```python
client = create_hda_client(api_key="your_key", debug=True)
```

## 📈 Common Use Cases

### 1. Network Performance Monitoring

Monitor overall network health and identify issues:

```python
# Get current network statistics
current_stats = client.get_stats_network_data(time_window_offset=0)
previous_stats = client.get_stats_network_data(time_window_offset=1)

# Compare performance month-over-month
# ... analysis code ...
```

### 2. Individual Street Analysis

Deep dive into specific street performance:

```python
# Analyze a problematic street
street_data = client.get_time_series_data(
    street_code="STREET_123",
    from_time=datetime.now() - timedelta(days=30),
    time_aggregation="HOURS_1",
    value_type="speed"
)

# Identify patterns, anomalies, etc.
```

### 3. KPI Dashboard

Build executive dashboards with KPI data:

```python
# Get KPI data for dashboard
kpi_data = client.get_kpi_overall_data(
    kpi_id="network_performance_kpi",
    from_time=datetime.now() - timedelta(days=7),
    to_time=datetime.now()
)
```

### 4. Geographic Analysis

Analyze performance by geographic regions:

```python
# Get available geohash tiles
network_info = client.get_stats_network_data()
tiles = network_info['availableTiles']

# Analyze each region
for tile in tiles:
    regional_data = client.get_stats_streets_data(selected_tile=tile)
    # ... process regional data ...
```

## 🚨 Error Handling

The client provides comprehensive error handling:

```python
from ptv_flows_hda_client import HdaApiError

try:
    data = client.get_time_series_data(street_code="invalid")
except HdaApiError as e:
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
    if e.response_data:
        print(f"Response: {e.response_data}")
```

Common error scenarios:
- **401 Unauthorized** - Invalid API key
- **400 Bad Request** - Invalid parameters
- **503 Service Unavailable** - Temporary service issues
- **Timeout** - Request took too long

## 🔍 Troubleshooting

### Connection Issues

1. **Check API Key**: Ensure your API key is valid and active
2. **Network Access**: Verify internet connection to `api.ptvgroup.tech`
3. **Firewall**: Ensure HTTPS traffic is allowed
4. **Debug Mode**: Enable debug logging to see detailed request/response info

### Data Issues

1. **Time Ranges**: Ensure time ranges are valid (max 1 hour for time slices)
2. **Street Identifiers**: Verify street codes, OpenLR codes, or ID/node combinations
3. **Geohash Tiles**: Use tiles from the network statistics endpoint
4. **KPI IDs**: Get valid KPI IDs from the KPI engineering API

### Performance Optimization

1. **Use Parquet Format**: More efficient for large datasets
2. **Pagination**: Use fromRow/toRow for large time slice downloads
3. **Caching**: Cache network metadata to avoid repeated calls
4. **Batch Processing**: Process data in chunks for memory efficiency

## 📚 Additional Resources

- **HDA API Documentation**: [OpenAPI Spec](https://api.ptvgroup.tech/meta/services/hda/v1/openapi.json)
- **KPI Engineering API**: [https://api.ptvgroup.tech/kpieng/v1](https://api.ptvgroup.tech/kpieng/v1)
- **PTV Flows Portal**: [https://ptvgroup.tech/flows/](https://ptvgroup.tech/flows/)
- **Support**: Contact PTV support for API-related issues

## 🤝 Contributing

This tutorial is part of the PTV Flows tutorials collection. To contribute:

1. Follow the existing code patterns and documentation style
2. Add tests for new functionality
3. Update this README for any new features
4. Ensure compatibility with the existing tutorial structure

## 📄 License

This tutorial follows the same license terms as the PTV Flows tutorials collection.

---

**Next Steps**: Run `python example.py` to test your setup and explore the API capabilities!