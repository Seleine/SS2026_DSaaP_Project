import pytest
import geopandas as gpd
from shapely.geometry import Point, Polygon
from src.config import buffer_around_home
from src.remove_home_points import remove_home_points


def test_remove_home_points_intersection():
    """
    Check that the intersection of home points is removed.
    """
    polygon = Polygon([(0, 0), (0, 2), (2, 2), (2, 0)])
    home_buffer = gpd.GeoSeries([polygon], crs=2056)

    data = gpd.GeoDataFrame(
        geometry=[
            Point(1, 1),  # inside
            Point(2, 1),  # boundary
            Point(3, 3),  # outside
        ],
        crs=2056,
    )

    result = remove_home_points(data, home_buffer)

    assert len(result) == 1
    assert result.geometry.iloc[0].equals(Point(3, 3))


def test_buffer_around_home_from_config_is_used():
    # Home location
    home_point = Point(0, 0)

    # Buffer created using config value
    home_buffer = gpd.GeoSeries(
        [home_point.buffer(buffer_around_home)],
        crs=2056,
    )

    # Points relative to the configured radius
    data = gpd.GeoDataFrame(
        geometry=[
            Point(buffer_around_home - 1, 0),  # inside
            Point(buffer_around_home + 1, 0),  # outside
        ],
        crs=2056,
    )

    result = remove_home_points(data, home_buffer)

    # Only the outside point should remain
    assert len(result) == 1
    assert result.geometry.iloc[0].equals(Point(buffer_around_home + 1, 0))


def test_null_geometry_raises(home_buffer):
    data = gpd.GeoDataFrame(
        geometry=[None],
        crs=2056,
    )

    with pytest.raises(ValueError, match="null geometries"):
        remove_home_points(data, home_buffer)


def test_null_geometry_in_data_raises(home_buffer):
    data = gpd.GeoDataFrame(
        geometry=[Point(0, 0), None],
        crs=2056,
    )
    with pytest.raises(ValueError, match="null geometries"):
        remove_home_points(data, home_buffer)


def test_empty_home_buffer_raises(sample_gdf):
    home_buffer = gpd.GeoSeries([], crs=2056)

    with pytest.raises(ValueError, match="empty"):
        remove_home_points(sample_gdf, home_buffer)


def test_only_first_home_buffer_geometry_is_used():
    # First buffer (used)
    buffer_1 = Point(0, 0).buffer(2)

    # Second buffer (ignored)
    buffer_2 = Point(100, 100).buffer(2)

    home_buffer = gpd.GeoSeries(
        [buffer_1, buffer_2],
        crs=2056,
    )

    data = gpd.GeoDataFrame(
        geometry=[
            Point(1, 1),  # intersects buffer_1 → removed
            Point(100, 100),  # intersects buffer_2 → should remain
        ],
        crs=2056,
    )

    result = remove_home_points(data, home_buffer)

    assert len(result) == 1
    assert result.geometry.iloc[0].equals(Point(100, 100))
