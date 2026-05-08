import shapely
import pytest
import geopandas as gpd
from src.kde import calculate_kde_from_gps_points
from conftest import sample_gdf

def test_create_static_column_raises_if_data_is_not_geodataframe():
    with pytest.raises(TypeError):
        calculate_kde_from_gps_points(data="not a geodataframe", variable_name="test")


def test_create_static_column_raises_if_variable_name_not_str():
    with pytest.raises(TypeError):
        calculate_kde_from_gps_points(data=sample_gdf, variable_name=123)


def test_returns_geodataframe(sample_gdf):
    result = calculate_kde_from_gps_points(sample_gdf, variable_name="test")
    assert isinstance(result, gpd.GeoDataFrame)


def test_raises_if_percentiles_is_not_list(sample_gdf):
    with pytest.raises(TypeError, match="list"):
        calculate_kde_from_gps_points(
            data=sample_gdf, variable_name="test", percentiles=(95, 75)
        )


def test_raises_if_percentiles_contains_non_int(sample_gdf):
    with pytest.raises(TypeError, match="list"):
        calculate_kde_from_gps_points(
            data=sample_gdf, variable_name="test", percentiles=[95.0, 75.0]
        )


def test_raises_if_grid_size_is_not_int(sample_gdf):
    with pytest.raises(TypeError, match="int"):
        calculate_kde_from_gps_points(
            data=sample_gdf, variable_name="test", grid_size=200.0
        )


def test_raises_if_percentiles_out_of_range(sample_gdf):
    with pytest.raises(ValueError, match="between 1 and 100"):
        calculate_kde_from_gps_points(
            data=sample_gdf, variable_name="test", percentiles=[95, 0]
        )


def test_default_percentiles_returns_five_rows(sample_gdf):
    result = calculate_kde_from_gps_points(sample_gdf, variable_name="test")
    assert len(result) == 5


def test_crs_is_preserved(sample_gdf):
    result = calculate_kde_from_gps_points(sample_gdf, variable_name="test")
    assert result.crs == sample_gdf.crs


def test_area_km2_is_positive(sample_gdf):
    result = calculate_kde_from_gps_points(sample_gdf, variable_name="test")
    assert (result["area_km2"] > 0).all()


def test_percentiles_column_values(sample_gdf):
    result = calculate_kde_from_gps_points(sample_gdf, variable_name="test")
    assert set(result["percent"]) == {95, 75, 50, 25, 10}


def test_raises_on_fewer_than_50_points():
    small_gdf = gpd.GeoDataFrame(
        geometry=[shapely.Point(2_600_000, 1_200_000)] * 10, crs="EPSG:2056"
    )
    with pytest.raises(ValueError, match="50 GPS points"):
        calculate_kde_from_gps_points(small_gdf, variable_name="test")
