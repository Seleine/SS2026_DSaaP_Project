import pytest
import geopandas as gpd
from src.summary_table import summary_table
import pandas as pd
import os


def test_summary_table(sample_layer, capsys):
    summary_table(data=sample_layer, datetime_col="time", table_name="table")

    captured = capsys.readouterr()

    output = captured.out

    assert (
        output == ""
    )  # Because we produce a html now, this is always empty before rendering!

def test_summary_table_returns_expected_dataframe(sample_layer):
    table = summary_table(data=sample_layer, datetime_col="time", table_name="table")

    assert isinstance(table, pd.DataFrame)

    expected_columns = [
        "Month",
        "Median Interval (min)",
        "Mean Interval (min)",
        "Min Interval (s)",
        "Max Interval (h)",
        "Count (points)",
        "Count < 9 min",
        "Proportion (%)",
    ]
    assert list(table.columns) == expected_columns
    assert len(table) > 0


def test_summary_table_raises_if_data_is_not_geodataframe():
    with pytest.raises(TypeError):
        summary_table(
            data="not a geodataframe", datetime_col="time", table_name="table"
        )


def test_summary_table_raises_if_datetime_col_not_str():
    gdf = gpd.GeoDataFrame()
    with pytest.raises(TypeError):
        summary_table(data=gdf, datetime_col=123, table_name="table")


def test_summary_table_raises_if_table_name_not_str():
    gdf = gpd.GeoDataFrame()
    with pytest.raises(TypeError):
        summary_table(data=gdf, datetime_col="time", table_name=123)


def test_summary_table_generates_html(sample_layer):
    path = "./quality_control/table.html"

    if os.path.exists(path):
        os.remove(path)

    summary_table(
        data=sample_layer,
        datetime_col="time",
        table_name="table",
    )

    assert os.path.exists(path)
