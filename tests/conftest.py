import pytest
import numpy as np
import geopandas as gpd
import pandas as pd
import shapely
from shapely.geometry import Point, Polygon
from tests._factories import make_sample_layer

@pytest.fixture
def sample_gdf():
    rng = np.random.default_rng(seed=42)  # deterministic
    x = rng.normal(
        loc=2_600_000, scale=1000, size=100
    )  # create sample EPSG:2056 coords
    y = rng.normal(loc=1_200_000, scale=1000, size=100)
    geometry = [shapely.Point(xi, yi) for xi, yi in zip(x, y)]
    return gpd.GeoDataFrame(geometry=geometry, crs="EPSG:2056")


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


@pytest.fixture
def sample_layer():
    return make_sample_layer(crs=2056)


@pytest.fixture
def home_buffer():
    polygon = Point(0, 0).buffer(2)
    return gpd.GeoSeries([polygon], crs=2056)