import geopandas as gpd
import shapely
import datetime as datetime
import numpy as np


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
