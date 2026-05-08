import numpy as np
import folium
import pytest
import geopandas as gpd
from src.kde_plot import plot_kde
from conftest import sample_kde_result


def test_plot_kde_raises_if_data_is_not_geodataframe():
    with pytest.raises(TypeError):
        plot_kde(data="not a geodataframe", plot_name="test")


def test_plot_kde_raises_if_plot_name_is_not_str(sample_kde_result):
    with pytest.raises(TypeError):
        plot_kde(data=sample_kde_result, plot_name=123)


def test_plot_kde_raises_if_required_columns_missing(sample_kde_result):
    with pytest.raises(ValueError):
        plot_kde(data=sample_kde_result.drop(columns=["area_km2"]), plot_name="test")


def test_plot_kde_raises_if_data_is_empty():
    empty = gpd.GeoDataFrame({"geometry": [], "area_km2": [], "Variable": []}, crs=2056)
    with pytest.raises(ValueError):
        plot_kde(data=empty, plot_name="test")


def test_plot_kde_raises_if_area_km2_is_not_numeric(sample_kde_result):
    sample_kde_result["area_km2"] = "not a number"
    with pytest.raises(ValueError):
        plot_kde(data=sample_kde_result, plot_name="test")


def test_plot_kde_raises_if_area_km2_contains_nan(sample_kde_result):
    sample_kde_result.loc[0, "area_km2"] = np.nan
    with pytest.raises(ValueError):
        plot_kde(data=sample_kde_result, plot_name="test")


def test_plot_kde_raises_if_crs_is_none(sample_kde_result):
    sample_kde_result = sample_kde_result.set_crs(None, allow_override=True)
    with pytest.raises(ValueError):
        plot_kde(data=sample_kde_result, plot_name="test")


def test_plot_kde_saves_html_and_returns_map(sample_kde_result, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("webbrowser.open", lambda url: None)

    result = plot_kde(data=sample_kde_result, plot_name="test")

    assert (tmp_path / "plots" / "test.html").exists()
    assert isinstance(result, folium.Map)



