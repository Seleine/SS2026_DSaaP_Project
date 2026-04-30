import shapely
import pytest
import geopandas as gpd
from datetime import datetime
import numpy as np
from geopandas.testing import assert_geodataframe_equal
from src.static_not_static import create_static_column


def test_create_static_column_should_return_new_geodataframe_when_input_valid():
    # Arrange
    sample_geom = gpd.GeoSeries([shapely.Point(2684961.287, 1246073.33), shapely.Point(2684806.122, 1246003.058),
                                 shapely.Point(2684828.182, 1245955.671)], crs=2056)
    sample_data = {
        "track_seg_point_id": [1, 2, 3],
        "time": [datetime.fromisoformat("2024-04-01 09:49:55+02:00"), datetime.fromisoformat("2024-04-01 09:59:38+02:00"), datetime.fromisoformat("2024-04-01 10:09:37+02:00")],
        "Month": ["April", "April", "April"],
        "dayphase": ["Daytime", "Daytime", "Daytime"],
        "geometry": sample_geom,
        "timelag": [583.0, 599.0, np.nan],
        "steplength": [170.336, 52.270, np.nan],
        "speed_ms": [0.292, 0.087, np.nan],
        "speed_kmh": [1.051, 0.313, np.nan]
    }
    sample_layer = gpd.GeoDataFrame(sample_data)

    # Act
    data = create_static_column(
        data=sample_layer,
        buffer=8
    )

    # Assert
    expected = gpd.GeoDataFrame({
        **sample_data, # unpacks dictionaries into keyword arguments
        "static": gpd.pd.array(["Not Static", "Not Static", "Not Static"], dtype=gpd.pd.StringDtype())
        },
        crs = 2056)

    assert_geodataframe_equal(data, expected, check_like=True)


def test_create_static_column_raises_if_data_is_not_geodataframe():
    with pytest.raises(TypeError):
        create_static_column(data="not a geodataframe", buffer=8)


def test_create_static_column_raises_if_buffer_is_not_int():
    gdf = gpd.GeoDataFrame()
    with pytest.raises(TypeError):
        create_static_column(data=gdf, buffer="not int")