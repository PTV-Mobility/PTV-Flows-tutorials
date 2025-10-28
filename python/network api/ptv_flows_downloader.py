#!/usr/bin/env python3
"""
PTV Flows Network Downloader

This script downloads network data from PTV Flows API, filters it by a user-specified
bounding box, and saves the results in both CSV and TopoJSON formats.

Usage:
    python ptv_flows_downloader.py [--api-key API_KEY] [--staging] [--output-dir OUTPUT_DIR]

Author: Generated from FlowsNetMatching-v6.ipynb
"""

import argparse
import sys
import os
import json
from typing import Optional, Tuple
import gzip
import io
import logging

import requests
import pandas as pd
import geopandas as gpd
from shapely import wkb
from shapely.geometry import Point, box
import flows_network_v1_pb2 as flows_network


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_bounding_box_from_user() -> Tuple[float, float, float, float]:
    """
    Prompts the user to input bounding box coordinates.
    
    Returns:
        Tuple of (min_lon, min_lat, max_lon, max_lat)
    """
    print("Please enter the bounding box coordinates:")
    print("Format: minimum longitude, minimum latitude, maximum longitude, maximum latitude")
    print("Example: 2.3, 48.8, 2.4, 48.9 (for central Paris)")
    
    while True:
        try:
            coords_input = input("Enter coordinates (min_lon, min_lat, max_lon, max_lat): ")
            coords = [float(x.strip()) for x in coords_input.split(',')]
            
            if len(coords) != 4:
                raise ValueError("Please provide exactly 4 coordinates")
            
            min_lon, min_lat, max_lon, max_lat = coords
            
            # Validate coordinate ranges
            if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
                raise ValueError("Longitude must be between -180 and 180")
            if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
                raise ValueError("Latitude must be between -90 and 90")
            if min_lon >= max_lon:
                raise ValueError("Minimum longitude must be less than maximum longitude")
            if min_lat >= max_lat:
                raise ValueError("Minimum latitude must be less than maximum latitude")
            
            return min_lon, min_lat, max_lon, max_lat
            
        except ValueError as e:
            print(f"Invalid input: {e}")
            print("Please try again.")


def download_flows_message(api_key: str, debug: bool = False) -> bytes:
    """
    Downloads the network message from PTV Flows API.
    
    Args:
        api_key: PTV API key
        debug: Whether to save downloaded data to file
        
    Returns:
        Raw protobuf data as bytes
    """
    url = "https://api.ptvgroup.tech/flows/map/v1/streets"
    
    headers = {
        "apiKey": api_key,
        "Accept": "application/gzip"
    }
    
    logger.info(f"Downloading from {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    if debug:
        # Save the content to a file
        with open("street_flows.gz", "wb") as f:
            f.write(response.content)
        logger.info("Saved downloaded data to street_flows.gz")
        
        # Read the content from the gzip file
        with gzip.open("street_flows.gz", "rb") as f:
            data = f.read()
    else:
        # Directly read the content from the response
        with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
            data = f.read()
    
    logger.info(f"Downloaded {len(data)} bytes of data")
    return data


def deserialize_message(data: bytes):
    """
    Deserializes the protobuf message.
    
    Args:
        data: Raw protobuf data
        
    Returns:
        Deserialized Network object
    """
    network = flows_network.Network()
    network.ParseFromString(data)
    return network


def convert_wkb_to_wkt(wkb_data: bytes) -> str:
    """
    Converts WKB (Well-Known Binary) to WKT (Well-Known Text).
    
    Args:
        wkb_data: WKB geometry data
        
    Returns:
        WKT string representation
    """
    geom = wkb.loads(wkb_data)
    return geom.wkt


def filter_network_by_bbox(network_flows, bbox: Tuple[float, float, float, float]) -> pd.DataFrame:
    """
    Filters the network data by bounding box and converts to DataFrame.
    
    Args:
        network_flows: Deserialized network object
        bbox: Tuple of (min_lon, min_lat, max_lon, max_lat)
        
    Returns:
        GeoDataFrame with filtered streets
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    bbox_geom = box(min_lon, min_lat, max_lon, max_lat)
    
    logger.info(f"Filtering {len(network_flows.street)} streets by bounding box: {bbox}")
    
    # Extract data from all streets
    streets_data = []
    for street in network_flows.street:
        try:
            # Convert WKB to Shapely geometry
            street_geom = wkb.loads(street.shape)
            
            # Check if street intersects with bounding box
            if street_geom.intersects(bbox_geom):
                wkt_shape = convert_wkb_to_wkt(street.shape)
                
                # Extract street attributes
                street_data = {
                    'id': street.id,
                    'from_node_id': street.from_node_id,
                    # OpenLR is stored as bytes in the protobuf; decode to UTF-8 text
                    # (it typically contains a base64/text representation). Previously
                    # the code used .hex() which produced a hex string. Decode so the
                    # output matches the original textual OpenLR value.
                    'openlr': street.openlr.decode('utf-8') if street.openlr else None,
                    'functional_road_class': street.functional_road_class,
                    'form_of_way': street.form_of_way,
                    'free_flow_speed_kmph': street.free_flow_speed_kmph,
                    'shape_wkt': wkt_shape,
                    'name': street.name if hasattr(street, 'name') and street.name else None,
                    'geometry': street_geom
                }
                streets_data.append(street_data)
                
        except Exception as e:
            logger.warning(f"Error processing street {street.id}: {e}")
            continue
    
    logger.info(f"Found {len(streets_data)} streets within bounding box")
    
    if not streets_data:
        logger.warning("No streets found within the specified bounding box")
        return gpd.GeoDataFrame()
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(streets_data, geometry='geometry')
    
    # Set CRS (assuming WGS84)
    gdf.set_crs('EPSG:4326', inplace=True)
    
    return gdf


def save_to_csv(gdf: gpd.GeoDataFrame, output_path: str):
    """
    Saves GeoDataFrame to CSV format.
    
    Args:
        gdf: GeoDataFrame to save
        output_path: Output file path
    """
    if gdf.empty:
        logger.warning("No data to save to CSV")
        return
    
    # Create a copy for CSV (remove geometry column, keep WKT)
    csv_df = gdf.drop('geometry', axis=1).copy()
    csv_df.to_csv(output_path, index=False)
    logger.info(f"Saved {len(csv_df)} records to {output_path}")


def save_to_topojson(gdf: gpd.GeoDataFrame, output_path: str):
    """
    Saves GeoDataFrame to TopoJSON format.
    
    Args:
        gdf: GeoDataFrame to save
        output_path: Output file path
    """
    if gdf.empty:
        logger.warning("No data to save to TopoJSON")
        return
    
    try:
        # First save as GeoJSON, then convert to TopoJSON
        geojson_path = output_path.replace('.topojson', '.geojson')
        
        # Prepare data for GeoJSON (remove shape_wkt column if present)
        gdf_for_export = gdf.drop('shape_wkt', axis=1, errors='ignore').copy()
        
        # Save as GeoJSON first
        gdf_for_export.to_file(geojson_path, driver='GeoJSON')
        
        # Try to convert to TopoJSON using topojson library
        try:
            import topojson as tp
            # Read the GeoJSON and convert to TopoJSON
            with open(geojson_path, 'r') as f:
                geojson_data = json.load(f)
            
            # Convert to TopoJSON
            topology = tp.Topology(geojson_data, prequantize=False)
            
            # Save TopoJSON
            with open(output_path, 'w') as f:
                json.dump(topology.to_dict(), f, indent=2)
            
            # Clean up temporary GeoJSON file
            os.remove(geojson_path)
            logger.info(f"Saved {len(gdf_for_export)} records to {output_path}")
            
        except ImportError:
            logger.warning("topojson library not available. Saving as GeoJSON instead.")
            # Rename the GeoJSON file to indicate it's not TopoJSON
            final_path = output_path.replace('.topojson', '.geojson')
            os.rename(geojson_path, final_path)
            logger.info(f"Saved {len(gdf_for_export)} records to {final_path} (GeoJSON format)")
            
    except Exception as e:
        logger.error(f"Error saving TopoJSON: {e}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Download and (optionally) filter PTV Flows network data and export to CSV/TopoJSON')
    parser.add_argument('--api-key', type=str,
                        help='PTV API key. Can also be provided via PTV_API_KEY environment variable.')
    parser.add_argument('--output-dir', type=str, default='.',
                        help='Output directory for files (default: current directory)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode (saves raw downloaded data)')
    parser.add_argument('--bbox', type=str,
                        help='Bounding box as min_lon,min_lat,max_lon,max_lat (no spaces). If provided, skips interactive prompt')
    parser.add_argument('--no-filter', action='store_true',
                        help='Do not filter by bounding box; process the entire network (may be large)')
    
    args = parser.parse_args()
    
    # Default API key (updated)
    default_api_key = os.environ.get('PTV_API_KEY', "change_me_to_your_api_key")
    api_key = args.api_key or default_api_key
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        # Determine bounding box behaviour
        if args.no_filter:
            # full-world bbox — effectively no filtering
            bbox = (-180.0, -90.0, 180.0, 90.0)
            logger.info("--no-filter set: processing entire network (world bbox)")
        elif args.bbox:
            try:
                coords = [float(x) for x in args.bbox.split(',')]
                if len(coords) != 4:
                    raise ValueError('Expected 4 comma-separated numeric values')
                min_lon, min_lat, max_lon, max_lat = coords
                # basic validation
                if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
                    raise ValueError('Longitude must be between -180 and 180')
                if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
                    raise ValueError('Latitude must be between -90 and 90')
                if min_lon >= max_lon or min_lat >= max_lat:
                    raise ValueError('min values must be strictly less than max values')
                bbox = (min_lon, min_lat, max_lon, max_lat)
                logger.info(f"Using bbox from --bbox: {bbox}")
            except Exception as e:
                logger.error(f"Invalid --bbox value: {e}")
                sys.exit(2)
        else:
            # Interactive prompt (existing behaviour)
            bbox = get_bounding_box_from_user()
        
        # Download data from PTV Flows API
        logger.info("Downloading data from PTV Flows API...")
        data = download_flows_message(api_key, debug=args.debug)
        
        # Deserialize the protobuf message
        logger.info("Deserializing network data...")
        network_flows = deserialize_message(data)
        
        # Filter by bounding box
        logger.info("Filtering network data by bounding box...")
        gdf = filter_network_by_bbox(network_flows, bbox)
        
        if gdf.empty:
            logger.error("No data found within the specified bounding box. Exiting.")
            sys.exit(1)
        
        # Generate output file names
        bbox_str = f"{bbox[0]}_{bbox[1]}_{bbox[2]}_{bbox[3]}"
        csv_path = os.path.join(args.output_dir, f"ptv_flows_network_{bbox_str}.csv")
        topojson_path = os.path.join(args.output_dir, f"ptv_flows_network_{bbox_str}.topojson")
        
        # Save to CSV
        logger.info("Saving to CSV...")
        save_to_csv(gdf, csv_path)
        
        # Save to TopoJSON
        logger.info("Saving to TopoJSON...")
        save_to_topojson(gdf, topojson_path)
        
        logger.info("Download and processing completed successfully!")
        logger.info(f"Files saved:")
        logger.info(f"  CSV: {csv_path}")
        logger.info(f"  TopoJSON: {topojson_path}")
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()