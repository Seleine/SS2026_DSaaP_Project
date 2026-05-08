import shapely
import pytest
import geopandas as gpd
from src.bar_plot_counts import barplot_counts
from conftest import sample_gdf_with_month

def test_barplot_counts_raises_if_data_is_not_geodataframe():
    with pytest.raises(TypeError):
        barplot_counts(data="not a geodataframe", x_variable="x", title="title", plot_name="plot")


def test_barplot_counts_raises_if_x_variable_is_not_str(sample_gdf_with_month):
    with pytest.raises(TypeError):
        barplot_counts(data=sample_gdf_with_month, x_variable=123, title="title", plot_name="plot")


def test_barplot_counts_raises_if_title_is_not_str(sample_gdf_with_month):
    with pytest.raises(TypeError):
        barplot_counts(data=sample_gdf_with_month, x_variable="Month", title=123, plot_name="plot")


def test_barplot_counts_raises_if_plot_name_is_not_str(sample_gdf_with_month):
    with pytest.raises(TypeError):
        barplot_counts(data=sample_gdf_with_month, x_variable="Month", title="title", plot_name=123)


def test_barplot_counts_raises_if_x_variable_not_in_columns(sample_gdf_with_month):
    with pytest.raises(ValueError):
        barplot_counts(data=sample_gdf_with_month, x_variable="nonexistent", title="title", plot_name="plot")


def test_barplot_counts_saves_png(sample_gdf_with_month, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("webbrowser.open", lambda url: None)

    barplot_counts(data=sample_gdf_with_month, x_variable="Month", title="title", plot_name="test")

    assert (tmp_path / "quality_control" / "barplot_count_data_points_test.png").exists()