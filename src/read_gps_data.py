import geopandas as gpd
import pandas as pd
import glob
import config
import os

def read_gps_data(file_path: str, gpx_layer: str, time_zone: str) -> gpd.GeoDataFrame:
    """
    Read and merge all GPX files from a directory into a single GeoDataFrame.

    Parameters
    ----------
    file_path : str
        Path to the directory containing the .gpx files.
    gpx_layer : str
        GPX layer to read, e.g. "track_points" or "tracks".
    time_zone : str
        Target time zone for the time column, e.g. "Europe/Zurich".
        Must be a valid tz database string.

    Returns
    -------
    gpd.GeoDataFrame
        A merged GeoDataFrame containing all track points with:
        - time       : timezone-aware datetime column
        - month_num  : integer month number (1–12)
        - Month      : ordered categorical month name (January–December)
        - geometry   : point geometries from the GPX files
    """

    # check if directory exists
    if not os.path.isdir(file_path):
        raise NotADirectoryError(f"Directory not found: '{file_path}'")
    # check if any .gpx files exist in the directory
    files = glob.glob(f"{file_path}/*.gpx")
    if not files:
        raise FileNotFoundError(f"No .gpx files found in: '{file_path}'")
    # check if time zone is valid
    try:
        import zoneinfo
        zoneinfo.ZoneInfo(time_zone)
    except zoneinfo.ZoneInfoNotFoundError:
        raise ValueError(f"Invalid time zone: '{time_zone}'. Use a valid tz database string, e.g. 'Europe/Zurich'.")
    # check if gpx_layer is valid
    valid_layers = ["track_points", "tracks", "waypoints", "routes"]
    if gpx_layer not in valid_layers:
        raise ValueError(f"Invalid layer: '{gpx_layer}'. Choose from {valid_layers}.")

    # list all .gpx files in the directory
    files = glob.glob(f"{file_path}/*.gpx")

    # read all files and store in a list
    data_list = [gpd.read_file(f, layer=gpx_layer) for f in files]

    # concatenate all GeoDataFrames into one
    merged_data = gpd.pd.concat(data_list, ignore_index=True)

    merged_data = merged_data[config.columns_of_choice]

    # ensure correct data type and time zone for time column
    merged_data["time"] =  pd.to_datetime(merged_data["time"]).dt.tz_convert(time_zone)

    # remove duplicated times
    merged_data = merged_data.drop_duplicates(subset=["time"])

    # extract month from date
    merged_data["Month"] = pd.to_datetime(merged_data["time"]).dt.month_name().str[:]

    # ensure correct order of months
    month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    merged_data["Month"] = pd.Categorical(merged_data["Month"], categories=month_order, ordered=True)

    # ensure correct geometry column
    merged_data = merged_data.set_geometry("geometry")

    # ensure correct CRS
    merged_data = merged_data.to_crs(config.CRS)

    if len(merged_data) < 50:
        raise ValueError(
            f"Only {len(merged_data)} GPS points found after cleaning. At least 50 are required for reliable KDE estimation.")

    return merged_data