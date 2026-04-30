import geopandas as gpd


def _buffers_intersect(data: gpd.GeoDataFrame, idx_a: int, idx_b: int) -> bool:
    """
    Check whether two buffers at given positions intersect.

    Parameters
    ----------
    data: gpd.GeoDataFrame
        GeoDataFrame containing a 'geom_buffer' column with buffer geometries.
    idx_a: int
        Positional index of the first buffer.
    idx_b: int
        Positional index of the second buffer.

    Returns
    -------
    bool
        True if the two buffers intersect, False otherwise.
    """
    if "geom_buffer" not in data.columns:
        raise ValueError("GeoDataFrame must contain a 'geom_buffer' column.")
    if not (0 <= idx_a < len(data)) or not (0 <= idx_b < len(data)):
        raise IndexError(f"Indices {idx_a} and {idx_b} must be within bounds of the GeoDataFrame (len={len(data)}).")

    return data["geom_buffer"].iloc[idx_a].intersects(data["geom_buffer"].iloc[idx_b])


def create_static_column(data: gpd.GeoDataFrame, buffer: int) -> gpd.GeoDataFrame:
    """
    Classify each GPS point as 'Static' or 'Not Static' based on buffer intersection.

    A point is considered static if its buffer intersects with the buffer of either
    the current reference point or the next point in the sequence.

    Parameters
    ----------
    data: gpd.GeoDataFrame
        GeoDataFrame with a valid geometry column representing GPS tracking points.
    buffer: int
        Buffer distance in the units of the GeoDataFrame's CRS (e.g. metres for EPSG:2056).

    Returns
    -------
    gpd.GeoDataFrame
        The input GeoDataFrame with two additional columns:
        - 'geom_buffer': buffer geometries around each point.
        - 'static': classification of each point as 'Static' or 'Not Static'.

    Raises
    ------
    TypeError
        If `data` is not a GeoDataFrame or `buffer` is not an integer.
    ValueError
        If `data` is empty or has no valid geometry column.
    """
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError(f"Expected a GeoDataFrame, got {type(data).__name__}.")
    if not isinstance(buffer, int):
        raise TypeError(f"Buffer must be an integer, got {type(buffer).__name__}.")
    if data.empty:
        raise ValueError("GeoDataFrame is empty.")
    if data.geometry is None:
        raise ValueError("GeoDataFrame must have a valid geometry column.")

    data["geom_buffer"] = data.geometry.buffer(buffer)
    data["static"] = None

    id = 0

    for i in range(len(data)):
        if i > 0 and _buffers_intersect(data, i, id):
            data.at[data.index[i], "static"] = "Static"

        elif i > 0 and i + 1 < len(data) and _buffers_intersect(data, i, i + 1):
            data.at[data.index[i], "static"] = "Static"
            id = i

        else:
            data.at[data.index[i], "static"] = "Not Static"
            id = i

    data = data.drop("geom_buffer", axis=1)

    data["static"] = data["static"].astype(gpd.pd.StringDtype())  # add before return

    return data