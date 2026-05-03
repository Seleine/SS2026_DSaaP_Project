import shapely
import pytest
import geopandas as gpd
from datetime import datetime
import numpy as np
from geopandas.testing import assert_geodataframe_equal
from src.speed import calculate_timelag_steplength_speed


def test_calculate_timelag_steplength_speed_should_return_new_geodataframe_when_input_valid():
    # Arrange
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
    }
    sample_layer = gpd.GeoDataFrame(sample_data)

    # Act
    data = calculate_timelag_steplength_speed(
        data=sample_layer, datetime_col="time", geometry_col="geometry"
    )

    # Assert
    expected = gpd.GeoDataFrame(
        {
            **sample_data,  # unpacks dictionaries into keyword arguments
            "timelag": [583.0, 599.0, np.nan],
            "steplength": [170.336, 52.270, np.nan],
            "speed_ms": [0.292, 0.087, np.nan],
            "speed_kmh": [1.051, 0.313, np.nan],
        }
    )

    assert_geodataframe_equal(data, expected, check_like=True)


def test_calculate_timelag_steplength_speed_raises_if_data_is_not_geodataframe():
    with pytest.raises(TypeError):
        calculate_timelag_steplength_speed(
            data="not a geodataframe", datetime_col="time", geometry_col="geometry"
        )


def test_calculate_timelag_steplength_speed_raises_if_datetime_col_is_not_string():
    gdf = gpd.GeoDataFrame()
    with pytest.raises(TypeError):
        calculate_timelag_steplength_speed(
            data=gdf, datetime_col=123, geometry_col="geometry"
        )


def test_calculate_timelag_steplength_speed_raises_if_geometry_col_is_not_string():
    gdf = gpd.GeoDataFrame()
    with pytest.raises(TypeError):
        calculate_timelag_steplength_speed(
            data=gdf, datetime_col="time", geometry_col=123
        )
