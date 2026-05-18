import geopandas as gpd


def remove_home_points(
    data: gpd.GeoDataFrame, home_buffer: gpd.GeoSeries
) -> gpd.GeoDataFrame:
    """
    Remove GPS tracking points that fall within the home buffer zone.

    Parameters
    ----------
    data : gpd.GeoDataFrame
        GeoDataFrame containing GPS tracking points.
    home_buffer : gpd.GeoSeries
        GeoSeries containing the home buffer polygon.

    Returns
    -------
    gpd.GeoDataFrame
        The input GeoDataFrame with all points inside the home buffer removed.

    Raises
    ------
    TypeError
        If ``data`` is not a GeoDataFrame, or ``home_buffer`` is not a GeoSeries.
    ValueError
        If ``data`` or ``home_buffer`` is empty, their CRS do not match, or
        either contains null geometries.
    """
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError(
            f"Expected a GeoDataFrame for 'data', got {type(data).__name__}."
        )
    if not isinstance(home_buffer, gpd.GeoSeries):
        raise TypeError(
            f"Expected a GeoSeries for 'home_buffer', got {type(home_buffer).__name__}."
        )
    if data.empty:
        raise ValueError("'data' GeoDataFrame is empty.")
    if home_buffer.empty:
        raise ValueError("'home_buffer' GeoDataFrame is empty.")
    if data.crs != home_buffer.crs:
        raise ValueError(
            f"CRS mismatch: 'data' is {data.crs}, 'home_buffer' is {home_buffer.crs}. Reproject before calling this function."
        )
    if data.geometry.isnull().any():
        raise ValueError("'data' contains null geometries.")
    if home_buffer.geometry.isnull().any():
        raise ValueError("'home_buffer' contains null geometries.")

    home_points = data.intersects(home_buffer.geometry.iloc[0])

    data = data[~home_points]

    return data
