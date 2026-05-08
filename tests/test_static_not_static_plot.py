import pytest
import geopandas as gpd
from src.static_not_static_plot import sample_plot_static_not_static


def test_sample_plot_static_not_static_raises_if_data_is_not_geodataframe():
    with pytest.raises(TypeError):
        sample_plot_static_not_static(
            data="not a geodataframe",
            start_date="2024-04-01 00:00:00",
            end_date="2024-04-01 18:00:00",
            time_zone="Europe/Zurich"
        )


def test_create_static_column_raises_if_start_date_not_str(sample_gdf):
    with pytest.raises(TypeError):
        sample_plot_static_not_static(
            data=sample_gdf,
            start_date=123,
            end_date="2024-04-01 18:00:00",
            time_zone="Europe/Zurich"
        )


def test_create_static_column_raises_if_end_date_not_str(sample_gdf):
    with pytest.raises(TypeError):
        sample_plot_static_not_static(
            data=sample_gdf,
            start_date="2024-04-01 00:00:00",
            end_date=123,
            time_zone="Europe/Zurich"
        )


def test_create_static_column_raises_if_time_zone_not_str(sample_gdf):
    with pytest.raises(TypeError):
        sample_plot_static_not_static(
            data=sample_gdf,
            start_date="2024-04-01 00:00:00",
            end_date="2024-04-01 18:00:00",
            time_zone=123
        )


def test_sample_plot_static_not_static_raises_if_data_is_empty():
    with pytest.raises(ValueError):
        sample_plot_static_not_static(
            data=gpd.GeoDataFrame(),
            start_date="2024-04-01 00:00:00",
            end_date="2024-04-01 18:00:00",
            time_zone="Europe/Zurich"
        )


def test_sample_plot_static_not_static_saves_and_opens(sample_layer_with_static, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # redirect file writes to temp dir
    monkeypatch.setattr("webbrowser.open", lambda url: None)

    sample_plot_static_not_static(
        data=sample_layer_with_static,
        start_date="2024-04-01 09:00:00",
        end_date="2024-04-01 11:00:00",
        time_zone="Europe/Zurich"
    )

    assert (tmp_path / "plots" / "sample_plot_static.html").exists()