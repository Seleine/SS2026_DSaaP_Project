import geopandas as gpd
import pandas as pd
from datetime import datetime

def summary_table(data: gpd.GeoDataFrame, datetime_col: datetime) -> pd.DataFrame:
    """
    Create a summary table of the data to get an overview of the data quality.

    Args:
        data: Input GeoDataFrame.
        datetime_col: Input datetime column of type datetime.

    Returns:
        DataFrame: Pandas DataFrame of the table.

    Raises:
        TypeError: If either argument is the wrong data type.
    """
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError("Argument data must be gpd.GeoDataFrame")
    elif not isinstance(datetime_col, datetime):
        raise TypeError("Argument datetime_col must be a datetime object")

    data = data.sort_values(by=datetime_col)

    data_no_geo = pd.DataFrame(data.drop(columns=data.geometry.name))
    data_no_geo = data_no_geo.rename(columns={'month': 'Month'})

    table = (data_no_geo.groupby("Month").agg(
            **{"Median Interval (min)": ("timestamp", lambda x: round(x.median() / 60, 2))},
            **{"Mean Interval (min)":   ("timestamp", lambda x: round(x.mean() / 60, 2))},
            **{"Min Interval (s)":      ("timestamp", "min")},
            **{"Max Interval (h)":      ("timestamp", lambda x: round(x.max() / 3600, 2))},
            **{"Count (points)":        ("timestamp", "count")},
            **{"Count < 9 min":         ("timestamp", lambda x: (x < 540).sum())},
            **{"Proportion (%)":        ("timestamp", lambda x: round((x < 540).sum() / len(x), 2) * 100)},
        )
        .reset_index()
    )

    return table


