import geopandas as gpd
import folium
from folium.plugins import GroupedLayerControl
import webbrowser
import branca.colormap as cm
from utils.output import get_output_dir


def collect_feature_groups(
    data_wgs: gpd.GeoDataFrame, colourmap: cm.LinearColormap
) -> list[folium.FeatureGroup]:
    """
    Takes the reprojected GeoDataFrame and the scaled colourmap, returns
    a list of folium FeatureGroup objects (one per variable).

    Parameters:
    data: gpd.GeoDataFrame: containing the KDE polygons. Must include:
            - geometry: Polygon or MultiPolygon geometries.
            - area_km2: Numeric column with the area_km2 of each polygon (km²).
            - Variable: Categorical column used to split layers.

    Returns:
    folium.FeatureGroup: The constructed folium feature groups.
    """

    feature_groups = []
    # variable_name = e.g. "variable1"
    # subset = the two rows where Variable == "variable1" (poly1 and multi)
    for variable_name, subset in data_wgs.groupby("Variable"):
        fg = folium.FeatureGroup(name=variable_name, show=False)

        folium.GeoJson(
            subset,
            style_function=lambda feature: {
                # feature is a GeoJSON-style Python dict that folium passes in, and feature["properties"]["area_km2"]
                # reads that polygon's area_km2 value from it
                "fillColor": colourmap(feature["properties"]["area_km2"]),
                # the colourmap then converts that number into a hex colour string like "#fd8d3c"
                "fillOpacity": 0.4,
                "color": "darkgrey",
                "weight": 1,
            },
            highlight_function=lambda _: {  # called when the user hovers over a polygon
                "color": "white",
                "weight": 2,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["area_km2"], aliases=["area_km2:"]
            ),  # small popup while hovering
        ).add_to(
            fg
        )  # attaches the whole GeoJson layer to the FeatureGroup so it becomes part of that variable's toggle layer.

        feature_groups.append(fg)

    return feature_groups


def get_data_extend(data_wgs: gpd.GeoDataFrame) -> list[list[float]]:
    """
    Fit map to data extent.

    Parameters:
    data: gpd.GeoDataFrame: containing the KDE polygons.

    Returns:
    list[list[float]]: Bounding box as [[min_lat, min_lon], [max_lat, max_lon]].
    """

    bounds = data_wgs.total_bounds
    return [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]


def plot_kde(data: gpd.GeoDataFrame, plot_name: str) -> folium.Map:
    """
    Plot kernel density estimation (KDE) home ranges as an interactive leaflet map.

    Polygons are grouped by the 'Variable' column and rendered as mutually exclusive radio-button layers, coloured
    by area_km2 size. The resulting map is saved as an HTML file and opened in the
    default browser.

    Parameters:
    data: gpd.GeoDataFrame: containing the KDE polygons. Must include:
            - geometry: Polygon or MultiPolygon geometries.
            - area_km2: Numeric column with the area_km2 of each polygon (km²).
            - Variable: Categorical column used to split layers.
    plot_name: string of plot name

    Returns:
    folium.Map: The constructed folium map object.

    Raises:
    TypeError
        If `data` is not a GeoDataFrame.
    ValueError
        If required columns ('geometry', 'area_km2', 'Variable') are missing,
        or if the GeoDataFrame is empty.
    """
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError(f"Expected a GeoDataFrame, got {type(data).__name__}.")
    if not isinstance(plot_name, str):
        raise TypeError(
            f"Expected plot_name to be a str, got {type(plot_name).__name__}."
        )
    required_columns = {"geometry", "area_km2", "Variable"}
    missing = required_columns - set(data.columns)
    if missing:
        raise ValueError(f"Missing required column(s): {missing}.")
    if data.empty:
        raise ValueError("GeoDataFrame is empty.")
    if not gpd.pd.api.types.is_numeric_dtype(data["area_km2"]):
        raise ValueError("Column 'area_km2' must be numeric.")
    if data["area_km2"].isna().any():
        raise ValueError("Column 'area_km2' contains NaN values.")
    if data.crs is None:
        raise ValueError("GeoDataFrame has no CRS set.")

    # Change to EPSG:4326 for leaflet
    data_wgs = data.copy()
    data_wgs.geometry = data_wgs.geometry.make_valid()
    data_wgs = data_wgs.to_crs(epsg=4326)

    # stretch the colourmap to (YlOrRd_09) match your actual data range
    # largest area_km2 has the darkest colour and vice versa
    colourmap = cm.LinearColormap(
        colors=list(reversed(cm.linear.YlOrRd_09.colors)),
        vmin=data_wgs["area_km2"].min(),
        vmax=data_wgs["area_km2"].max(),
    )

    # Initialise folium map with default OSM tiles
    m = folium.Map()

    # Split GeoDataFrame by Variable, collect FeatureGroups
    feature_groups = collect_feature_groups(data_wgs=data_wgs, colourmap=colourmap)

    # add each feature group to the map
    for fg in feature_groups:
        fg.add_to(m)

    # GroupedLayerControl with exclusive_groups=True for radio-button behaviour
    GroupedLayerControl(
        groups={"Variables": feature_groups},
        exclusive_groups=True,
        collapsed=False,
    ).add_to(m)

    # Fit map to data extent
    m.fit_bounds(get_data_extend(data_wgs=data_wgs))

    plots_dir = get_output_dir()

    output_html = plots_dir / f"{plot_name}.html"
    m.save(output_html)
    output_html.touch()

    webbrowser.open(f"file://{output_html.resolve()}")

    return m
