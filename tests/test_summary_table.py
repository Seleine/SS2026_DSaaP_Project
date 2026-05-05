import shapely
import pytest
import geopandas as gpd
from datetime import datetime
import numpy as np
from src.summary_table import summary_table
from io import StringIO
import sys


def test_summary_table():
    # Arrange
    captured = StringIO()
    sys.stdout = captured

    sample_geom = gpd.GeoSeries(
        [
            shapely.Point(2684961.287, 1246073.33),
            shapely.Point(2684806.122, 1246003.058),
            shapely.Point(2684828.182, 1245955.671),
        ],
        crs=2056,
    )
    sample_data = {
        "track_seg_point_id": [1, 2, 3],
        "time": [
            datetime.fromisoformat("2024-04-01 09:49:55+02:00"),
            datetime.fromisoformat("2024-04-01 09:59:38+02:00"),
            datetime.fromisoformat("2024-04-01 10:09:37+02:00"),
        ],
        "Month": ["April", "April", "April"],
        "dayphase": ["Daytime", "Daytime", "Daytime"],
        "geometry": sample_geom,
        "timelag": [580.0, 600.0, 620.0],
        "steplength": [170.336, 52.270, np.nan],
        "speed_ms": [0.292, 0.087, np.nan],
        "speed_kmh": [1.051, 0.313, np.nan],
    }
    sample_layer = gpd.GeoDataFrame(sample_data)

    # Act
    summary_table(data=sample_layer, datetime_col="time", table_name="table")

    sys.stdout = sys.__stdout__
    output = captured.getvalue()

    # Assert
    assert "Month" in output
    assert "Median Interval (min)" in output
    assert "10.0" in output
    assert len(output) > 0


def test_summary_table_raises_if_data_is_not_geodataframe():
    with pytest.raises(TypeError):
        summary_table(data="not a geodataframe", datetime_col="time", table_name="table")


def test_summary_table_raises_if_buffer_is_not_int():
    gdf = gpd.GeoDataFrame()
    with pytest.raises(TypeError):
        summary_table(data=gdf, datetime_col=123, table_name="table")


def test_summary_table_raises_if_buffer_is_not_int():
    gdf = gpd.GeoDataFrame()
    with pytest.raises(TypeError):
        summary_table(data=gdf, datetime_col="time", table_name=123)
