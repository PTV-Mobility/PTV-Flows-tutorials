# PTV Flows HDA API - Test Suite

This directory contains tests for the HDA API client and utilities.

## Test Structure

### Unit Tests
- `test_hda_client.py` - Tests for the main HDA client functionality
- `test_data_processing.py` - Tests for data processing utilities

### Mock Responses
- `mock_responses/` - Mock API response data for offline testing

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_hda_client.py

# Run with coverage
python -m pytest tests/ --cov=ptv_flows_hda_client
```

## Test Data

Mock responses are provided for offline testing and development.

---

**Note**: Test suite will be implemented as part of Phase 3.
Currently, basic functionality testing is available through the setup script.