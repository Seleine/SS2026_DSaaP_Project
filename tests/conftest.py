import pytest
import numpy as np
import geopandas as gpd
import shapely

@pytest.fixture
def sample_gdf():
    rng = np.random.default_rng(seed=42)  # deterministic
    x = rng.normal(
        loc=2_600_000, scale=1000, size=100
    )  # create sample EPSG:2056 coords
    y = rng.normal(loc=1_200_000, scale=1000, size=100)
    geometry = [shapely.Point(xi, yi) for xi, yi in zip(x, y)]
    return gpd.GeoDataFrame(geometry=geometry, crs="EPSG:2056")