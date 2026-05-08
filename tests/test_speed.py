import pytest
import geopandas as gpd
import numpy as np
from geopandas.testing import assert_geodataframe_equal
from src.speed import calculate_timelag_steplength_speed


def test_calculate_timelag_steplength_speed_should_adds_columns_when_input_valid(
    sample_layer,
):
    # Act
    result = calculate_timelag_steplength_speed(
        data=sample_layer.copy(),  # important: avoid side effects
        datetime_col="time",
        geometry_col="geometry",
    )

    # Assert
    expected = sample_layer.copy()

    expected["timelag"] = [583.0, 599.0, np.nan]
    expected["steplength"] = [170.336, 52.270, np.nan]
    expected["speed_ms"] = [0.292, 0.087, np.nan]
    expected["speed_kmh"] = [1.051, 0.313, np.nan]

    assert_geodataframe_equal(result, expected, check_like=True)


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
