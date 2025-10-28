# PTV Flows HDA API - Configuration Files

This directory contains configuration files for HDA API scripts and workflows.

## Configuration Structure

### Default Configuration
- `default_config.json` - Base configuration with default parameters

### Example Configurations
- `example_configs/` - Pre-configured examples for common use cases

## Usage

Configuration files use JSON format and can be passed to scripts:

```bash
python scripts/kpi_monitor.py --config config/monitoring_config.json
python example.py --config config/example_configs/rome_analysis.json
```

---

**Note**: Configuration files will be created as part of Phase 2 implementation.
Currently, all configuration is handled via script parameters and environment variables.