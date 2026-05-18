import geopandas as gpd


def _calculate_timediff_seconds(later: gpd.GeoSeries, now: gpd.pd.Series) -> float:
    """
    Calculate the difference between two datetime objects in seconds.

    Parameter
    ---------
        later (datetime): The later Series.
        now (datetime): The earlier Series.

    Returns
    -------
        float: The difference in seconds. Negative if 'later' is before 'now'.

    Raises
    ------
        TypeError: If either argument is not a Series.
    """
    if not isinstance(later, gpd.pd.Series) or not isinstance(now, gpd.pd.Series):
        raise TypeError("Both arguments must be gpd.GeoSeries")

    timediff = later - now

    return timediff.dt.total_seconds()


def _calculate_distance_by_element(
    geom_a: gpd.GeoSeries, geom_b: gpd.GeoSeries
) -> float:
    """
    Calculate the distance by element.

    Parameter
    ---------
        geom_a: The first Point.
        geom_b: The second Point.

    Returns
    -------
        float: Distance by element

    Raises
    ------
        TypeError: If either argument is not a GeoPandas Series object.
    """
    if not isinstance(geom_a, gpd.GeoSeries) or not isinstance(geom_b, gpd.GeoSeries):
        raise TypeError("Both arguments must be gpd.GeoSeries")

    distdiff = geom_a.distance(geom_b)

    return distdiff


def calculate_timelag_steplength_speed(
    data: gpd.GeoDataFrame, datetime_col: str, geometry_col: str
) -> gpd.GeoDataFrame:
    """
    Calculate the time lag, steplength, and speed between two GPS points.

    Parameter
    ---------
        data: Input GeoDataFrame.
        datetime_col: Input datetime column of type string.
        geometry_col: Input GeoSeries of geometry of type string.

    Returns
    -------
        GeoDataFrame: New GeoDataFrame with added columns.

    Raises
    ------
        TypeError: If either argument is the wrong data type.
    """
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError("Argument data must be gpd.GeoDataFrame")
    elif not isinstance(datetime_col, str):
        raise TypeError("Argument datetime_col must be a string")
    elif not isinstance(geometry_col, str):
        raise TypeError("Argument geometry must be a string")

    data = data.sort_values(by=datetime_col)

    data["timelag"] = _calculate_timediff_seconds(
        later=data[datetime_col].shift(-1), now=data[datetime_col]
    )
    data["steplength"] = round(
        _calculate_distance_by_element(
            geom_a=data[geometry_col], geom_b=data[geometry_col].shift(-1)
        ),
        3,
    )
    data["speed_ms"] = round(data["steplength"] / data["timelag"], 3)
    data["speed_kmh"] = round(data["speed_ms"] * 3.6, 3)

    return data
