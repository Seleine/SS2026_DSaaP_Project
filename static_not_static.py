import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString
import customised_variables
import webbrowser


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

    return data


def _filter_by_time(data: gpd.GeoDataFrame, start_date: str, end_date: str, time_zone: str) -> gpd.GeoDataFrame:
    """
    Filter a GeoDataFrame to a specific time range.

    Parameters
    ----------
    data: gpd.GeoDataFrame
        GeoDataFrame containing a 'time' column with timezone-aware timestamps.
    start_date: str
        Start of the time range (inclusive), e.g. '2024-04-01 00:00:00'.
    end_date: str
        End of the time range (exclusive), e.g. '2024-04-01 18:00:00'.
    time_zone: str
        Timezone string, e.g. 'Europe/Zurich'.

    Returns
    -------
    gpd.GeoDataFrame
        Filtered GeoDataFrame containing only rows within the time range.

    Raises
    ------
    TypeError
        If `data` is not a GeoDataFrame.
    ValueError
        If `data` is empty, 'time' column is missing, or start_date >= end_date.
    """
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError(f"Expected a GeoDataFrame, got {type(data).__name__}.")
    if data.empty:
        raise ValueError("GeoDataFrame is empty.")
    if "time" not in data.columns:
        raise ValueError("GeoDataFrame must contain a 'time' column.")

    return data[
        (data["time"] >= pd.Timestamp(start_date, tz=time_zone)) &
        (data["time"] < pd.Timestamp(end_date, tz=time_zone))].copy()


def _create_track_line(data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Create a LineString GeoDataFrame connecting GPS points in temporal order.

    Parameters
    ----------
    data: gpd.GeoDataFrame
        GeoDataFrame with a valid geometry column representing GPS points,
        assumed to be ordered by time.

    Returns
    -------
    gpd.GeoDataFrame
        Single-row GeoDataFrame containing a LineString connecting all points.

    Raises
    ------
    TypeError
        If `data` is not a GeoDataFrame.
    ValueError
        If `data` has fewer than 2 points, as a LineString requires at least 2.
    """
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError(f"Expected a GeoDataFrame, got {type(data).__name__}.")
    if len(data) < 2:
        raise ValueError(f"At least 2 points are required to create a LineString, got {len(data)}.")

    return gpd.GeoDataFrame(
        geometry=[LineString(data.geometry.tolist())],
        crs=data.crs
    )


def _build_static_map(data: gpd.GeoDataFrame):
    """
    Build an interactive folium map with track, buffers, and static/non-static points.

    Parameters
    ----------
    data: gpd.GeoDataFrame
        GeoDataFrame containing at minimum a geometry column, a 'geom_buffer' column,
        a 'static' column, a 'track_seg_point_id' column, and a 'time' column.

    Returns
    -------
    folium.Map
        Interactive map with three layers: track line, buffers, and classified points.

    Raises
    ------
    TypeError
        If `data` is not a GeoDataFrame.
    ValueError
        If any of the required columns are missing.
    """
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError(f"Expected a GeoDataFrame, got {type(data).__name__}.")

    required_columns = {"geom_buffer", "static", "track_seg_point_id", "time"}
    missing = required_columns - set(data.columns)
    if missing:
        raise ValueError(f"GeoDataFrame is missing required columns: {missing}.")
    data_line = _create_track_line(data)

    m = data_line.explore(color="black", name="Track")
    data["geom_buffer"].explore(m=m, color="blue", name="Buffer")
    data.explore(
        m=m,
        column="static",
        categories=["Static", "Not Static"],
        cmap=["red", "black"],
        tooltip=["track_seg_point_id", "static", "time"],
        name="Points"
    )
    return m


def sample_plot_static_not_static(data: gpd.GeoDataFrame, start_date: str, end_date: str, time_zone: str = customised_variables.time_zone) -> None:
    """
    Generate and open an interactive map of static vs. non-static GPS points.

    Parameters
    ----------
    data: gpd.GeoDataFrame
        GeoDataFrame containing GPS tracking points with required columns:
        'time', 'geometry', 'geom_buffer', 'static', 'track_seg_point_id'.
    start_date: str
        Start of the time range (inclusive), e.g. '2024-04-01 00:00:00'.
    end_date: str
        End of the time range (exclusive), e.g. '2024-04-01 18:00:00'.
    time_zone: str
        Timezone string, e.g. 'Europe/Zurich'. Defaults to the project timezone.

    Returns
    -------
    None
        Saves 'sample_plot_static.html' to the working directory and opens it.

    Raises
    ------
    TypeError
        If `data` is not a GeoDataFrame.
    ValueError
        If `data` is empty or required columns are missing.
    """
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError(f"Expected a GeoDataFrame, got {type(data).__name__}.")
    if data.empty:
        raise ValueError("GeoDataFrame is empty.")

    data_sample_plot = _filter_by_time(data, start_date, end_date, time_zone)
    m = _build_static_map(data_sample_plot)
    m.save("sample_plot_static.html")
    webbrowser.open("sample_plot_static.html")
