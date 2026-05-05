import shapely
import pytest
import geopandas as gpd
from datetime import datetime
import numpy as np
from geopandas.testing import assert_geodataframe_equal
from src.static_not_static import create_static_column


    # Act
    data = create_static_column(data=sample_layer, buffer=8)

    # Assert
    expected = gpd.GeoDataFrame(
        {
            **sample_data,  # unpacks dictionaries into keyword arguments
            "static": gpd.pd.array(
                ["Not Static", "Not Static", "Not Static"], dtype=gpd.pd.StringDtype()
            ),
        },
        crs=2056,
    )

    assert_geodataframe_equal(
        data.drop(columns="geom_buffer"),
        expected,
        check_like=True,
    )


def test_create_static_column_raises_if_data_is_not_geodataframe():
    with pytest.raises(TypeError):
        create_static_column(data="not a geodataframe", buffer=8)


def test_create_static_column_raises_if_buffer_is_not_int():
    gdf = gpd.GeoDataFrame()
    with pytest.raises(TypeError):
        create_static_column(data=gdf, buffer="not int")
