import pytest
import numpy as np
import geopandas as gpd
import pandas as pd
import shapely
from shapely.geometry import Point
from tests._factories import make_sample_layer, make_sample_kde_result


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
def sample_gdf_with_dayphase_times(sample_gdf):
    """
    Create a sample GeoDataFrame with a 'time' column with times spanning across the day to test calculate_phases_of_the_day.
    """
    gdf = sample_gdf.head(4).copy()

    gdf["time"] = pd.to_datetime(
        [
            "2024-01-01 05:30",  # before sunrise
            "2024-01-01 07:00",  # daytime
            "2024-01-01 18:30",  # after sunset
            "2024-01-01 23:00",  # night
        ],
        utc=True,
    ).tz_convert("Europe/Zurich")

    return gdf


@pytest.fixture
def sample_layer():
    return make_sample_layer(crs=2056).copy()


@pytest.fixture
def sample_layer_with_static(sample_layer):

    sample_layer["geom_buffer"] = sample_layer.geometry.buffer(50)
    sample_layer["static"] = ["Static", "Not Static", "Static"]
    return sample_layer


def sample_gdf_with_month(sample_gdf):
    rng = np.random.default_rng(seed=42)
    gdf = sample_gdf.copy()
    gdf["Month"] = rng.choice(["January", "February", "March"], size=len(gdf))
    return gdf


@pytest.fixture
def home_buffer():
    polygon = Point(0, 0).buffer(2)
    return gpd.GeoSeries([polygon], crs=2056)


@pytest.fixture
def sample_kde_result():
    return make_sample_kde_result(crs=2056).copy()
