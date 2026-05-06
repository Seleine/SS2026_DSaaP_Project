import pytest
import numpy as np
import geopandas as gpd
from datetime import datetime
import pandas as pd
import shapely
from shapely.geometry import Point, Polygon

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


def make_sample_layer(crs: int = 2056) -> gpd.GeoDataFrame:
    geometry = gpd.GeoSeries(
        [
            shapely.Point(2684961.287, 1246073.33),
            shapely.Point(2684806.122, 1246003.058),
            shapely.Point(2684828.182, 1245955.671),
        ],
        crs=crs,
    )

    data = {
        "track_seg_point_id": [1, 2, 3],
        "time": [
            datetime.fromisoformat("2024-04-01 09:49:55+02:00"),
            datetime.fromisoformat("2024-04-01 09:59:38+02:00"),
            datetime.fromisoformat("2024-04-01 10:09:37+02:00"),
        ],
        "Month": ["April", "April", "April"],
        "dayphase": ["Daytime", "Daytime", "Daytime"],
        "geometry": geometry,
        "timelag": [583.0, 599.0, np.nan],
        "steplength": [170.336, 52.270, np.nan],
        "speed_ms": [0.292, 0.087, np.nan],
        "speed_kmh": [1.051, 0.313, np.nan],
    }

    return gpd.GeoDataFrame(data, crs=crs)


@pytest.fixture
def sample_layer():
    return make_sample_layer(crs=2056)


@pytest.fixture
def home_buffer():
    polygon = Point(0, 0).buffer(2)
    return gpd.GeoSeries([polygon], crs=2056)