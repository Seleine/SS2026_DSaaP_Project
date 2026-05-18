import geopandas as gpd
import pandas as pd
import os


def summary_table(
    data: gpd.GeoDataFrame, datetime_col: str, table_name: str
) -> pd.DataFrame:
    """
    Create a summary table of the data to get an overview of data quality.

    Parameters
    ----------
    data : gpd.GeoDataFrame
        The input GeoDataFrame.
    datetime_col : str
        The name of the column containing datetime values.
    table_name : str
        The name used when saving the table.

    Returns
    -------
    pd.DataFrame
        A DataFrame summarising the data quality.

    Raises
    ------
    TypeError
        If ``data`` is not a GeoDataFrame, or ``datetime_col`` or ``table_name``
        are not strings.
    """
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError("Argument data must be gpd.GeoDataFrame")
    elif not isinstance(datetime_col, str) or not isinstance(table_name, str):
        raise TypeError("Argument datetime_col and table_name must be string")

    data = data.sort_values(by=datetime_col)

    data_no_geo = pd.DataFrame(data.drop(columns=data.geometry.name))
    data_no_geo = data_no_geo.rename(columns={"month": "Month"})

    table = (
        data_no_geo.groupby("Month")
        .agg(
            **{
                "Median Interval (min)": (
                    "timelag",
                    lambda x: round(x.median() / 60, 2),
                )
            },
            **{"Mean Interval (min)": ("timelag", lambda x: round(x.mean() / 60, 2))},
            **{"Min Interval (s)": ("timelag", "min")},
            **{"Max Interval (h)": ("timelag", lambda x: round(x.max() / 3600, 2))},
            **{"Count (points)": ("timelag", "count")},
            **{"Count < 9 min": ("timelag", lambda x: (x < 540).sum())},
            **{
                "Proportion (%)": (
                    "timelag",
                    lambda x: round((x < 540).sum() / len(x), 2) * 100,
                )
            },
        )
        .reset_index()
    )

    if not os.path.exists("./quality_control"):
        os.mkdir("./quality_control")

    output_path = os.path.abspath(f"./quality_control/{table_name}.html")

    (
        table.style.set_table_styles(
            [
                {
                    "selector": "th",
                    "props": [
                        ("background-color", "#4CAF50"),
                        ("color", "white"),
                        ("padding", "8px"),
                    ],
                },
                {
                    "selector": "td",
                    "props": [("padding", "8px"), ("border", "1px solid #ddd")],
                },
                {
                    "selector": "tr:nth-child(even)",
                    "props": [("background-color", "#f2f2f2")],
                },
            ]
        )
        .hide(axis="index")
        .to_html(output_path)
    )

    return table
