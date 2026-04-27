from suncalc import get_times
import geopandas as gpd
import numpy as np

def calculate_phases_of_the_day(data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Assign a day phase label to each GPS point based on sun times.

    The function reprojects the data to WGS84 to calculate sun times,
    assigns a day phase to each point, then reprojects back to LV95.

    Parameters
    ----------
    data : gpd.GeoDataFrame
        GeoDataFrame in LV95 (EPSG:2056) with a timezone-aware
        datetime column named 'time'.

    Returns
    -------
    gpd.GeoDataFrame
        The input GeoDataFrame in LV95 (EPSG:2056) with an additional
        'dayphase' column containing one of:
        'Dawn', 'Daytime', 'Dusk', or 'Nighttime'.
    """
    # check if input is a GeoDataFrame
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError(f"Expected a GeoDataFrame, got {type(data).__name__}.")
    # check if 'time' column exists
    if "time" not in data.columns:
        raise ValueError("GeoDataFrame must contain a 'time' column.")
    # check if 'time' column is timezone-aware
    if data["time"].dt.tz is None:
        raise ValueError("The 'time' column must be timezone-aware.")
    # check if GeoDataFrame is empty
    if data.empty:
        raise ValueError("GeoDataFrame is empty.")
    # check if geometry column exists and is valid
    if data.geometry.isnull().any():
        raise ValueError("GeoDataFrame contains null geometries.")

    data_wgs = data.to_crs(4326) # WGS84 needed for library suncalc

    sun_times = gpd.pd.DataFrame(
        get_times(
            data_wgs["time"].astype("datetime64[ns, UTC]"), # suncalc need time in ns precision
            data_wgs["geometry"].x,
            data_wgs["geometry"].y
        )
    ).reset_index(drop=True)

    t = data_wgs["time"].dt.tz_convert("UTC").reset_index(drop=True)

    conditions = [
        (sun_times["dawn"] <= t) & (t <= sun_times["sunrise"]),
        (sun_times["sunset"] <= t) & (t <= sun_times["dusk"]),
        (sun_times["sunrise"] <= t) & (t <= sun_times["sunset"]),
        (t < sun_times["dawn"]) | (t > sun_times["dusk"])
    ]
    choices = ["Dawn", "Dusk", "Daytime", "Nighttime"]

    data_wgs["dayphase"] = np.select(conditions, choices, default="Unknown")

    print("If all four day phases appear, each gps tracking point is correctly grouped", data_wgs["dayphase"].unique())

    return data_wgs.to_crs(2056)

