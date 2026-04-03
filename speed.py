from datetime import datetime
import geopandas as gpd

def calculate_timediff_seconds(later: datetime, now: datetime) -> float:
    """
    Calculate the difference between two datetime objects in seconds.

    Args:
        later (datetime): The later datetime object.
        now (datetime): The earlier datetime object.

    Returns:
        float: The difference in seconds. Negative if 'later' is before 'now'.

    Raises:
        TypeError: If either argument is not a datetime object.
    """
    if not isinstance(later, datetime) or not isinstance(now, datetime):
        raise TypeError("Both arguments must be datetime objects")

    timediff = later - now

    return float(timediff.total_seconds())


def calculate_distance_by_element(geom_a: gpd.GeoSeries, geom_b: gpd.GeoSeries) -> float:
    """
    Calculate the distance by element.

    Args:
        geom_a: The first Point.
        geom_b: The second Point.

    Returns:
        float:

    Raises:
        TypeError: If either argument is not a GeoPandas Series object.
    """
    if not isinstance(geom_a, gpd.GeoSeries) or not isinstance(geom_b, gpd.GeoSeries):
        raise TypeError("Both arguments must be gpd.GeoSeries")

    distdiff = geom_b - geom_a

    return float(distdiff)


def calculate_timelag_steplength_speed(data: gpd.GeoDataFrame, datetime_col: datetime, geometry_col: gpd.GeoSeries) -> gpd.GeoDataFrame:
    """
    Calculate the time lag, steplength, and speed between two GPS points.

    Args:
        data: Input GeoDataFrame.
        datetime_col: Input datetime column of type datetime.
        geometry_col: Input GeoSeries of geometry of type gpd.GeoSeries.

    Returns:
        GeoDataFrame: New GeoDataFrame with added columns.

    Raises:
        TypeError: If either argument is the wrong data type.
    """
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError("Argument data must be gpd.GeoDataFrame")
    elif not isinstance(datetime_col, datetime):
        raise TypeError("Argument datetime_col must be a datetime object")
    elif not isinstance(geometry_col, gpd.GeoSeries):
        raise TypeError("Argument geometry must be gpd.GeoSeries")

    data = data.sort_values(by=datetime_col)

    data["timelag"] = calculate_timediff_seconds(later=data[datetime_col].shift(-1), now=data[datetime_col])
    data["steplength"] = calculate_distance_by_element(geom_a=data[geometry_col].shift(-1), geom_b=data[geometry_col])
    data["speed_ms"] = data["steplength"] / data["timelag"]
    data["speed_kmh"] = data["speed_ms"] * 3.6

    return data
