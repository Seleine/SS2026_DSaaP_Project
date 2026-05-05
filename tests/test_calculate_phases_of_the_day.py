
import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

import pytest
from test_kde import sample_gdf
from src.calculate_phases_of_the_day import calculate_phases_of_the_day

# Auxillary functions
@pytest.fixture
def sample_gdf_with_time(sample_gdf):
    """
    Create a sample GeoDataFrame with a 'time' column for testing calculate_phases_of_the_day.
    """
    gdf = sample_gdf.copy()
    gdf["time"] = pd.date_range(
        "2024-01-01 12:00",
        periods=len(gdf),
        freq="min",
        tz="Europe/Zurich",
    )
    return gdf

def fake_get_times(times, lon, lat):
    """
    A fake implementation of suncalc.get_times that returns fixed times for testing purposes.
    This dependency injection is not what we want to test. So, we are injecting the behavious:
    How do we compute sun times?

    Parameters
    ----------
    times : pd.Series
        A Series of timestamps for which to calculate sun times.
    lon : float
        Longitude of the location (not used in this fake implementation).
    lat : float
        Latitude of the location (not used in this fake implementation).

    Returns
    -------
    times with fixed offsets for dawn, sunrise, sunset, and dusk.
    """
    return {
        "dawn": times - pd.Timedelta(hours=1),
        "sunrise": times - pd.Timedelta(minutes=30),
        "sunset": times + pd.Timedelta(minutes=30),
        "dusk": times + pd.Timedelta(hours=1),
    }

# Actual test functions
def test_crs_preserved(sample_gdf_with_time):
    """
    Check that the CRS of the input GeoDataFrame is preserved in the output after calculating phases of the day.
    This ensures that the function does not alter the spatial reference system of the data, which is important for
    downstream spatial analyses.
    """
    result = calculate_phases_of_the_day(
        sample_gdf_with_time,
        get_sun_times=fake_get_times,
    )

    assert result.crs.to_epsg() == 2056


def test_row_count_preserved(sample_gdf_with_time):
    """
    Ensures that the number of rows in the output GeoDataFrame is the same as the input GeoDataFrame after calculating
    phases of the day.
    """
    result = calculate_phases_of_the_day(
        sample_gdf_with_time,
        get_sun_times=fake_get_times,
    )

    assert len(result) == len(sample_gdf_with_time)


def test_dayphase_values_valid(sample_gdf_with_time):
    """
    Check that the dayphase values are valid.
    """
    result = calculate_phases_of_the_day(
        sample_gdf_with_time,
        get_sun_times=fake_get_times,
    )

    allowed = {"Dawn", "Daytime", "Dusk", "Nighttime", "Unknown"}

    assert set(result["dayphase"]).issubset(allowed)


def test_missing_time_column_raises(sample_gdf_with_time):
    """
    Check that the missing time column raises an error.
    """
    gdf = sample_gdf_with_time.drop(columns=["time"])

    with pytest.raises(ValueError, match="time"):
        calculate_phases_of_the_day(
            gdf,
            get_sun_times=fake_get_times,
        )


def test_timezone_naive_time_raises(sample_gdf_with_time):
    """
    Check that the timezone-naive times are naive for calculating phases of the day.
    This ensures correct handling of timezones in the function.
    """
    gdf = sample_gdf_with_time.copy()
    gdf["time"] = gdf["time"].dt.tz_localize(None)

    with pytest.raises(ValueError, match="timezone-aware"):
        calculate_phases_of_the_day(
            gdf,
            get_sun_times=fake_get_times,
        )


def test_empty_geodataframe_raises():
    """
    Check that an empty geodataframe raises an error.
    """
    empty = gpd.GeoDataFrame(
        {"time": []},
        geometry=[],
        crs=2056,
    )

    with pytest.raises(ValueError, match="empty"):
        calculate_phases_of_the_day(
            empty,
            get_sun_times=fake_get_times,
        )
