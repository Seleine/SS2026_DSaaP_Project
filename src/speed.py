import geopandas as gpd


def _calculate_timediff_seconds(later: gpd.GeoSeries, now: gpd.pd.Series) -> float:
    """
    Calculate the difference between two datetime Series in seconds.

    Parameters
    ----------
    later : pd.Series
        The later datetime Series.
    now : pd.Series
        The earlier datetime Series.

    Returns
    -------
    pd.Series
        The difference in seconds. Negative if ``later`` is before ``now``.

    Raises
    ------
    TypeError
        If ``later`` or ``now`` are not datetime Series.
    """
    if not isinstance(later, gpd.pd.Series) or not isinstance(now, gpd.pd.Series):
        raise TypeError("Both arguments must be gpd.GeoSeries")

    timediff = later - now

    return timediff.dt.total_seconds()


def _calculate_distance_by_element(
    geom_a: gpd.GeoSeries, geom_b: gpd.GeoSeries
) -> float:
    """
    Calculate the element-wise distance between two geometry Series.

    Parameters
    ----------
    geom_a : gpd.GeoSeries
        The first Series of point geometries.
    geom_b : gpd.GeoSeries
        The second Series of point geometries.

    Returns
    -------
    pd.Series
        The element-wise distance between corresponding points.

    Raises
    ------
    TypeError
        If ``geom_a`` or ``geom_b`` are not GeoSeries objects.
    """
    if not isinstance(geom_a, gpd.GeoSeries) or not isinstance(geom_b, gpd.GeoSeries):
        raise TypeError("Both arguments must be gpd.GeoSeries")

    distdiff = geom_a.distance(geom_b)

    return distdiff


def calculate_timelag_steplength_speed(
    data: gpd.GeoDataFrame, datetime_col: str, geometry_col: str
) -> gpd.GeoDataFrame:
    """
    Calculate the time lag, step length, and speed between consecutive GPS points.

    Parameters
    ----------
    data : gpd.GeoDataFrame
        The input GeoDataFrame containing GPS points.
    datetime_col : str
        The name of the column containing datetime values.
    geometry_col : str
        The name of the column containing point geometries.

    Returns
    -------
    gpd.GeoDataFrame
        A new GeoDataFrame with added columns for time lag, step length, and speed.

    Raises
    ------
    TypeError
        If ``data`` is not a GeoDataFrame, or ``datetime_col`` or ``geometry_col``
        are not strings.
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
