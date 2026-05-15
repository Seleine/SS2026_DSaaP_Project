import pytest
import geopandas as gpd
from cat_movement_analysis.static_not_static import create_static_column


def test_create_static_column_marks_all_not_static(sample_layer):
    result = create_static_column(sample_layer, buffer=8)

    assert "static" in result.columns
    assert list(result["static"]) == [
        "Not Static",
        "Not Static",
        "Not Static",
    ]


def test_create_static_column_raises_if_data_is_not_geodataframe():
    with pytest.raises(TypeError):
        create_static_column(data="not a geodataframe", buffer=8)


def test_create_static_column_raises_if_buffer_is_not_int():
    gdf = gpd.GeoDataFrame()
    with pytest.raises(TypeError):
        create_static_column(data=gdf, buffer="not int")
