#!/usr/bin/env python3
"""
PTV Flows Historical Data API (HDA) Client

This module provides a comprehensive Python client for interacting with the 
PTV Flows Historical Data API. It supports all 9 endpoints across 5 categories:
- Time Slice Data
- Time Series Data  
- Statistical Network Data
- KPI Data
- Elaborated Data

The client handles authentication, multiple response formats (JSON, Parquet, CSV),
error handling, and provides convenient methods for data processing.

Author: PTV Flows Tutorial
Date: October 28, 2025
API Version: v1
"""

import requests
import pandas as pd
import json
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HdaApiError(Exception):
    """Custom exception for HDA API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class HdaClient:
    """
    PTV Flows Historical Data API Client
    
    Provides methods to interact with all HDA API endpoints:
    - Time slice data for bulk network analysis
    - Time series data for individual street analysis
    - Statistical data for network performance metrics
    - KPI data for performance indicators
    - Elaborated data for processed analytics
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.ptvgroup.tech/hda/v1", 
                 timeout: int = 30, debug: bool = False):
        """
        Initialize the HDA API client.
        
        Args:
            api_key (str): Your PTV API key for authentication
            base_url (str): Base URL for the HDA API (default: production endpoint)
            timeout (int): Request timeout in seconds (default: 30)
            debug (bool): Enable debug logging (default: False)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.debug = debug
        
        if debug:
            logger.setLevel(logging.DEBUG)
            
        # Validate API key
        if not api_key or api_key == "your_api_key_here":
            raise ValueError("Invalid API key. Please provide a valid PTV API key.")
            
        logger.info(f"HDA Client initialized with base URL: {self.base_url}")
        
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None, 
                     accept_header: str = "application/json") -> requests.Response:
        """
        Make an authenticated request to the HDA API.
        
        Args:
            endpoint (str): API endpoint path
            params (dict): Query parameters
            accept_header (str): Accept header for response format
            
        Returns:
            requests.Response: Raw HTTP response
            
        Raises:
            HdaApiError: If the API request fails
        """
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        headers = {
            'apiKey': self.api_key,
            'Accept': accept_header,
            'User-Agent': 'PTV-Flows-HDA-Python-Client/1.0'
        }
        
        if self.debug:
            logger.debug(f"Making request to: {url}")
            #logger.debug(f"Headers: {headers}")
            logger.debug(f"Params: {params}")
            
        try:
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            
            if self.debug:
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {response.headers}")
                
            # Handle different error cases
            if response.status_code == 401:
                raise HdaApiError("Authentication failed. Please check your API key.", 
                                response.status_code, response.text)
            elif response.status_code == 400:
                error_msg = "Bad request. Check your parameters."
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_msg = error_data['message']
                except:
                    error_msg = response.text
                raise HdaApiError(error_msg, response.status_code, response.text)
            elif response.status_code == 503:
                raise HdaApiError("Service temporarily unavailable. Please try again later.", 
                                response.status_code, response.text)
            elif response.status_code != 200:
                raise HdaApiError(f"API request failed with status {response.status_code}", 
                                response.status_code, response.text)
                
            return response
            
        except requests.exceptions.Timeout:
            raise HdaApiError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise HdaApiError("Connection error. Please check your internet connection.")
        except requests.exceptions.RequestException as e:
            raise HdaApiError(f"Request failed: {str(e)}")

    # =============================================================================
    # TIME SLICE DATA ENDPOINTS
    # =============================================================================
    
    def get_time_slice_data(self, from_time: Union[str, datetime], to_time: Optional[Union[str, datetime]] = None,
                           from_row: Optional[int] = None, to_row: Optional[int] = None,
                           output_format: str = "json") -> Union[pd.DataFrame, Dict, bytes]:
        """
        Get speed data for the entire network within a given time interval.
        
        Args:
            from_time (str|datetime): Start time (ISO 8601 format)
            to_time (str|datetime, optional): End time (max 1 hour interval)
            from_row (int, optional): Starting row index (1-based)
            to_row (int, optional): Ending row index (exclusive)
            output_format (str): Response format - "json", "parquet", or "csv"
            
        Returns:
            DataFrame, dict, or bytes depending on output_format
            
        Example:
            # Get last hour of data
            data = client.get_time_slice_data("2024-10-21T10:00:00Z", "2024-10-21T11:00:00Z")
        """
        params = {}
        
        # Handle datetime formatting
        if isinstance(from_time, datetime):
            params['fromTime'] = from_time.isoformat() + 'Z'
        else:
            params['fromTime'] = from_time
            
        if to_time:
            if isinstance(to_time, datetime):
                params['toTime'] = to_time.isoformat() + 'Z'
            else:
                params['toTime'] = to_time
                
        if from_row is not None:
            params['fromRow'] = from_row
        if to_row is not None:
            params['toRow'] = to_row
            
        # Set appropriate accept header
        accept_headers = {
            "json": "application/json",
            "parquet": "application/vnd.apache.parquet", 
            "csv": "application/octet-stream"
        }
        
        if output_format not in accept_headers:
            raise ValueError(f"Invalid output_format. Must be one of: {list(accept_headers.keys())}")
            
        accept_header = accept_headers[output_format]
        
        logger.info(f"Fetching time slice data from {params['fromTime']} to {params.get('toTime', 'auto')}")
        
        response = self._make_request("/time-slice/get", params, accept_header)
        
        # Process response based on format
        if output_format == "json":
            return response.json()
        elif output_format == "parquet":
            return pd.read_parquet(io.BytesIO(response.content))
        elif output_format == "csv":
            return pd.read_csv(io.BytesIO(response.content), compression='gzip')
        else:
            return response.content

    # =============================================================================
    # TIME SERIES DATA ENDPOINTS  
    # =============================================================================
    
    def get_time_series_data(self, from_time: Optional[Union[str, datetime]] = None,
                           to_time: Optional[Union[str, datetime]] = None,
                           street_code: Optional[str] = None, 
                           street_idno: Optional[int] = None,
                           street_from_node: Optional[int] = None,
                           openlr_code: Optional[str] = None,
                           time_aggregation: str = "HOURS_1",
                           value_type: str = "speed",
                           output_format: str = "json") -> Union[pd.DataFrame, Dict, bytes]:
        """
        Get time series speed data for a single network element.
        
        Args:
            from_time (str|datetime, optional): Start time (default: 3 days ago)
            to_time (str|datetime, optional): End time (default: 24 hours ago)
            street_code (str, optional): Internal street code identifier
            street_idno (int, optional): Model base street identifier
            street_from_node (int, optional): Model base from node (required with street_idno)
            openlr_code (str, optional): OpenLR code identifier
            time_aggregation (str): Time aggregation (MINUTES_5|15|30, HOURS_1, DAYS_1)
            value_type (str): Value type (speed|probeCount|travelTime)
            output_format (str): Response format - "json", "parquet", or "csv"
            
        Returns:
            DataFrame, dict, or bytes depending on output_format
            
        Example:
            # Get hourly speed data for a street
            data = client.get_time_series_data(
                street_code="ABC123",
                time_aggregation="HOURS_1",
                value_type="speed"
            )
        """
        params = {}
        
        # Handle datetime parameters
        if from_time:
            if isinstance(from_time, datetime):
                params['fromTime'] = from_time.isoformat() + 'Z'
            else:
                params['fromTime'] = from_time
                
        if to_time:
            if isinstance(to_time, datetime):
                params['toTime'] = to_time.isoformat() + 'Z'  
            else:
                params['toTime'] = to_time
                
        # Street identification (one of three methods required)
        if street_code:
            params['streetCode'] = street_code
        elif street_idno and street_from_node:
            params['streetIdno'] = street_idno
            params['streetFromNode'] = street_from_node
        elif openlr_code:
            params['openLrCode'] = openlr_code
        else:
            raise ValueError("One street identifier is required: street_code, (street_idno + street_from_node), or openlr_code")
            
        # Validation for aggregation and value type
        valid_aggregations = ["MINUTES_5", "MINUTES_15", "MINUTES_30", "HOURS_1", "DAYS_1"]
        valid_value_types = ["speed", "probeCount", "travelTime"]
        
        if time_aggregation not in valid_aggregations:
            raise ValueError(f"Invalid time_aggregation. Must be one of: {valid_aggregations}")
        if value_type not in valid_value_types:
            raise ValueError(f"Invalid value_type. Must be one of: {valid_value_types}")
            
        params['timeAggregation'] = time_aggregation
        params['valueType'] = value_type
        
        # Set appropriate accept header  
        accept_headers = {
            "json": "application/json",
            "parquet": "application/vnd.apache.parquet",
            "csv": "application/octet-stream"
        }
        
        accept_header = accept_headers.get(output_format, "application/json")
        
        logger.info(f"Fetching time series data for street identifier: {street_code or street_idno or openlr_code}")
        
        response = self._make_request("/time-series/get", params, accept_header)
        
        # Process response based on format
        if output_format == "json":
            return response.json()
        elif output_format == "parquet":
            return pd.read_parquet(io.BytesIO(response.content))
        elif output_format == "csv":
            return pd.read_csv(io.BytesIO(response.content), compression='gzip')
        else:
            return response.content

    # =============================================================================
    # STATISTICAL NETWORK DATA ENDPOINTS
    # =============================================================================
    
    def get_stats_streets_data(self, time_window_offset: int = 0, selected_tile: Optional[str] = None,
                              street_codes: Optional[List[str]] = None,
                              output_format: str = "json") -> Union[pd.DataFrame, Dict, bytes]:
        """
        Get statistical network data for streets.
        
        Args:
            time_window_offset (int): Time period offset (0=current month, 1=previous month, etc.)
            selected_tile (str, optional): Geohash tile filter
            street_codes (List[str], optional): Specific street codes to filter
            output_format (str): Response format - "json", "parquet"
            
        Returns:
            DataFrame, dict, or bytes depending on output_format
        """
        params = {'timeWindowOffset': time_window_offset}
        
        if selected_tile:
            params['selectedTile'] = selected_tile
        if street_codes:
            params['streetCodes'] = street_codes
            
        accept_header = "application/vnd.apache.parquet" if output_format == "parquet" else "application/json"
        
        logger.info(f"Fetching street statistics for time window offset: {time_window_offset}")
        
        response = self._make_request("/stats/streets/get", params, accept_header)
        
        if output_format == "json":
            return response.json()
        elif output_format == "parquet":
            return pd.read_parquet(io.BytesIO(response.content))
        else:
            return response.content
    
    def get_stats_freeflow_data(self, time_window_offset: int = 0, selected_tile: Optional[str] = None,
                               output_format: str = "json") -> Union[pd.DataFrame, Dict, bytes]:
        """
        Get free-flow speed statistical data.
        
        Args:
            time_window_offset (int): Time period offset
            selected_tile (str, optional): Geohash tile filter  
            output_format (str): Response format - "json", "parquet"
            
        Returns:
            DataFrame, dict, or bytes depending on output_format
        """
        params = {'timeWindowOffset': time_window_offset}
        
        if selected_tile:
            params['selectedTile'] = selected_tile
            
        accept_header = "application/vnd.apache.parquet" if output_format == "parquet" else "application/json"
        
        logger.info(f"Fetching free-flow statistics for time window offset: {time_window_offset}")
        
        response = self._make_request("/stats/freeflow/get", params, accept_header)
        
        if output_format == "json":
            return response.json()
        elif output_format == "parquet":
            return pd.read_parquet(io.BytesIO(response.content))
        else:
            return response.content
    
    def get_stats_network_data(self, time_window_offset: int = 0,
                              output_format: str = "json") -> Union[pd.DataFrame, Dict, bytes]:
        """
        Get network-wide statistical information including available geohash tiles.
        
        Args:
            time_window_offset (int): Time period offset
            output_format (str): Response format - "json", "parquet"
            
        Returns:
            DataFrame, dict, or bytes depending on output_format
        """
        params = {'timeWindowOffset': time_window_offset}
        
        accept_header = "application/vnd.apache.parquet" if output_format == "parquet" else "application/json"
        
        logger.info(f"Fetching network statistics for time window offset: {time_window_offset}")
        
        response = self._make_request("/stats/network/get", params, accept_header)
        
        if output_format == "json":
            return response.json()
        elif output_format == "parquet":
            return pd.read_parquet(io.BytesIO(response.content))
        else:
            return response.content

    # =============================================================================
    # KPI DATA ENDPOINTS
    # =============================================================================
    
    def get_kpi_overall_data(self, kpi_id: str, from_time: Union[str, datetime],
                            to_time: Union[str, datetime], output_format: str = "json") -> Union[pd.DataFrame, Dict, bytes]:
        """
        Get overall KPI results.
        
        Args:
            kpi_id (str): KPI identifier from KPI engineering API
            from_time (str|datetime): Start time
            to_time (str|datetime): End time  
            output_format (str): Response format - "json", "parquet"
            
        Returns:
            DataFrame, dict, or bytes depending on output_format
            
        Note:
            KPI IDs can be obtained from: https://api.ptvgroup.tech/kpieng/v1
        """
        params = {'kpiId': kpi_id}
        
        if isinstance(from_time, datetime):
            params['fromTime'] = from_time.isoformat() + 'Z'
        else:
            params['fromTime'] = from_time
            
        if isinstance(to_time, datetime):
            params['toTime'] = to_time.isoformat() + 'Z'
        else:
            params['toTime'] = to_time
            
        accept_header = "application/vnd.apache.parquet" if output_format == "parquet" else "application/json"
        
        logger.info(f"Fetching overall KPI data for KPI ID: {kpi_id}")
        
        response = self._make_request("/kpi/overall/get", params, accept_header)
        
        if output_format == "json":
            return response.json()
        elif output_format == "parquet":
            return pd.read_parquet(io.BytesIO(response.content))
        else:
            return response.content
    
    def get_kpi_detailed_data(self, kpi_id: str, from_time: Union[str, datetime],
                             to_time: Union[str, datetime], output_format: str = "json") -> Union[pd.DataFrame, Dict, bytes]:
        """
        Get detailed KPI analysis results.
        
        Args:
            kpi_id (str): KPI identifier from KPI engineering API
            from_time (str|datetime): Start time
            to_time (str|datetime): End time
            output_format (str): Response format - "json", "parquet"
            
        Returns:
            DataFrame, dict, or bytes depending on output_format
        """
        params = {'kpiId': kpi_id}
        
        if isinstance(from_time, datetime):
            params['fromTime'] = from_time.isoformat() + 'Z'
        else:
            params['fromTime'] = from_time
            
        if isinstance(to_time, datetime):
            params['toTime'] = to_time.isoformat() + 'Z'
        else:
            params['toTime'] = to_time
            
        accept_header = "application/vnd.apache.parquet" if output_format == "parquet" else "application/json"
        
        logger.info(f"Fetching detailed KPI data for KPI ID: {kpi_id}")
        
        response = self._make_request("/kpi/detailed/get", params, accept_header)
        
        if output_format == "json":
            return response.json()
        elif output_format == "parquet":
            return pd.read_parquet(io.BytesIO(response.content))
        else:
            return response.content

    # =============================================================================
    # ELABORATED DATA ENDPOINTS
    # =============================================================================
    
    def get_elaborated_by_hours_days_data(self, output_format: str = "json") -> Union[pd.DataFrame, Dict, bytes]:
        """
        Get elaborated data processed by hours and days patterns.
        
        Args:
            output_format (str): Response format - "json", "parquet"
            
        Returns:
            DataFrame, dict, or bytes depending on output_format
        """
        accept_header = "application/vnd.apache.parquet" if output_format == "parquet" else "application/json"
        
        logger.info("Fetching elaborated data by hours and days")
        
        response = self._make_request("/elaborated/byHoursAndDays/get", {}, accept_header)
        
        if output_format == "json":
            return response.json()
        elif output_format == "parquet":
            return pd.read_parquet(io.BytesIO(response.content))
        else:
            return response.content
    
    def get_elaborated_overall_data(self, output_format: str = "json") -> Union[pd.DataFrame, Dict, bytes]:
        """
        Get overall elaborated analytics data.
        
        Args:
            output_format (str): Response format - "json", "parquet"
            
        Returns:
            DataFrame, dict, or bytes depending on output_format
        """
        accept_header = "application/vnd.apache.parquet" if output_format == "parquet" else "application/json"
        
        logger.info("Fetching overall elaborated data")
        
        response = self._make_request("/elaborated/overall/get", {}, accept_header)
        
        if output_format == "json":
            return response.json()
        elif output_format == "parquet":
            return pd.read_parquet(io.BytesIO(response.content))
        else:
            return response.content

    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def test_connection(self) -> bool:
        """
        Test the API connection and authentication.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Use network stats endpoint as a lightweight test
            self.get_stats_network_data()
            logger.info("✅ API connection test successful")
            return True
        except Exception as e:
            logger.error(f"❌ API connection test failed: {str(e)}")
            return False
    
    def get_available_formats(self) -> List[str]:
        """
        Get list of supported output formats.
        
        Returns:
            List[str]: Available format types
        """
        return ["json", "parquet", "csv"]
    
    def format_datetime(self, dt: Union[str, datetime]) -> str:
        """
        Format datetime for API requests.
        
        Args:
            dt (str|datetime): Datetime to format
            
        Returns:
            str: ISO 8601 formatted datetime string
        """
        if isinstance(dt, datetime):
            return dt.isoformat() + 'Z'
        return dt


# Convenience function for creating client instances
def create_hda_client(api_key: str, staging: bool = False, debug: bool = False) -> HdaClient:
    """
    Convenience function to create an HDA client instance.
    
    Args:
        api_key (str): Your PTV API key
        staging (bool): Use staging environment (default: False for production)
        debug (bool): Enable debug logging (default: False)
        
    Returns:
        HdaClient: Configured client instance
    """
    base_url = "https://api.ptvgroup.tech/hda/v1"
    if staging:
        # Note: Replace with actual staging URL when available
        base_url = "https://api-staging.ptvgroup.tech/hda/v1"
        
    return HdaClient(api_key=api_key, base_url=base_url, debug=debug)


if __name__ == "__main__":
    # Basic usage example
    print("PTV Flows HDA API Client")
    print("========================")
    print("This is the core client library for the PTV Flows Historical Data API.")
    print("For examples and tutorials, run: python example.py")
    print()
    print("Quick usage:")
    print("  from ptv_flows_hda_client import create_hda_client")
    print("  client = create_hda_client('your_api_key_here')")
    print("  data = client.get_stats_network_data()")