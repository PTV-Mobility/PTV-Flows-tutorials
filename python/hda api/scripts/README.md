# PTV Flows HDA API - Advanced Scripts

This directory contains specialized analysis and utility scripts for the HDA API.

## Available Scripts

### 📊 Data Analysis
- `time_slice_demo.py` - Time slice data analysis and visualization
- `time_series_analysis.py` - Historical trend analysis and seasonal patterns
- `statistical_analyzer.py` - Network performance statistics and benchmarking

### 📈 Monitoring & KPIs
- `kpi_monitor.py` - KPI monitoring, alerting, and dashboard generation

### 🗺️ Geographic Analysis
- `geohash_explorer.py` - Geographic data exploration and tile analysis

### 🔧 Utilities
- `data_converter.py` - Format conversion and data processing utilities

## Usage

Each script can be run independently:

```bash
python scripts/time_series_analysis.py --help
python scripts/kpi_monitor.py --config config/monitoring.json
```

## Configuration

Scripts use configuration files from the `../config/` directory.

---

**Note**: These scripts are part of Phase 2 implementation and will be available soon.
For now, use the main `example.py` script to explore basic HDA API functionality.