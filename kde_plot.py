from shapely import MultiPolygon, Polygon
import geopandas as gpd
import folium
from folium.plugins import GroupedLayerControl
import os
import webbrowser
import branca.colormap as cm


def collect_feature_groups(data_wgs: gpd.GeoDataFrame, colourmap:  cm.LinearColormap) -> list[folium.FeatureGroup]:
    """
    Takes the reprojected GeoDataFrame and the scaled colourmap, returns
    a list of folium FeatureGroup objects (one per variable).

    Parameters:
    data: gpd.GeoDataFrame: containing the KDE polygons. Must include:
            - geometry: Polygon or MultiPolygon geometries.
            - area: Numeric column with the area of each polygon (km²).
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
                # feature is a GeoJSON-style Python dict that folium passes in, and feature["properties"]["area"]
                # reads that polygon's area value from it
                "fillColor": colourmap(feature["properties"]["area"]),
                # the colourmap then converts that number into a hex colour string like "#fd8d3c"
                "fillOpacity": 0.4,
                "color": "darkgrey",
                "weight": 1,
            },
            highlight_function=lambda _: { # called when the user hovers over a polygon
                "color": "white",
                "weight": 2,
            },
            tooltip=folium.GeoJsonTooltip(fields=["area"], aliases=["Area:"]), # small popup while hovering
        ).add_to(fg) # attaches the whole GeoJson layer to the FeatureGroup so it becomes part of that variable's toggle layer.

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

def plot_kde(data: gpd.GeoDataFrame) -> folium.Map:
    """
    Plot kernel density estimation (KDE) home ranges as an interactive leaflet map.

    Polygons are grouped by the 'Variable' column and rendered as mutually exclusive radio-button layers, coloured
    by area size. The resulting map is saved as an HTML file and opened in the
    default browser.

    Parameters:
    data: gpd.GeoDataFrame: containing the KDE polygons. Must include:
            - geometry: Polygon or MultiPolygon geometries.
            - area: Numeric column with the area of each polygon (km²).
            - Variable: Categorical column used to split layers.

    Returns:
    folium.Map: The constructed folium map object.

    Raises:
    TypeError
        If `data` is not a GeoDataFrame.
    ValueError
        If required columns ('geometry', 'area', 'Variable') are missing,
        or if the GeoDataFrame is empty.
    """
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError(f"Expected a GeoDataFrame, got {type(data).__name__}.")
    required_columns = {"geometry", "area", "Variable"}
    missing = required_columns - set(data.columns)
    if missing:
        raise ValueError(f"Missing required column(s): {missing}.")
    if data.empty:
        raise ValueError("GeoDataFrame is empty.")
    if not gpd.pd.api.types.is_numeric_dtype(data["area"]):
        raise ValueError("Column 'area' must be numeric.")
    if data["area"].isna().any():
        raise ValueError("Column 'area' contains NaN values.")
    if data.crs is None:
        raise ValueError("GeoDataFrame has no CRS set.")

    # Change to EPSG:4326 for leaflet
    data_wgs = data.copy()
    data_wgs.geometry = data_wgs.geometry.make_valid()
    data_wgs = data_wgs.to_crs(epsg=4326)

    # stretch the colourmap to (YlOrRd_09) match your actual data range
    # largest area has the darkest colour and vice versa
    colourmap = cm.LinearColormap(
        colors=list(reversed(cm.linear.YlOrRd_09.colors)),
        vmin=data_wgs["area"].min(),
        vmax=data_wgs["area"].max(),
    )

    # Initialise folium map with default OSM tiles
    m = folium.Map()

    # Split GeoDataFrame by Variable, collect FeatureGroups
    feature_groups = collect_feature_groups(data_wgs = data_wgs, colourmap = colourmap)

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
    m.fit_bounds(get_data_extend(data_wgs = data_wgs))

    output_html = os.path.abspath("home_range_explore.html")
    m.save(output_html)
    webbrowser.open(f"file://{output_html}")

    return m


# ------------------------------------------------------------------
# Example usage
# ------------------------------------------------------------------
poly1 = Polygon([
    (2682520, 1246750), (2682920, 1246650), (2683120, 1246950),
    (2682820, 1247150), (2682420, 1247050), (2682520, 1246750),
])
poly2 = Polygon([
    (2682500, 1246800), (2682900, 1246700), (2683100, 1247000),
    (2682800, 1247200), (2682400, 1247100), (2682500, 1246800),
])
poly3 = Polygon([
    (2682200, 1246200), (2682600, 1246100), (2682700, 1246400),
    (2682300, 1246500), (2682100, 1246350), (2682200, 1246200),
])
multi = MultiPolygon([poly2, poly3])

poly1_2 = Polygon([
    (2682720, 1246950), (2683120, 1246850), (2683320, 1247150),
    (2683020, 1247350), (2682620, 1247250), (2682720, 1246950),
])
poly2_2 = Polygon([
    (2682700, 1247000), (2683100, 1246900), (2683300, 1247200),
    (2683000, 1247400), (2682600, 1247300), (2682700, 1247000),
])
poly3_2 = Polygon([
    (2682400, 1246400), (2682800, 1246300), (2682900, 1246600),
    (2682500, 1246700), (2682300, 1246550), (2682400, 1246400),
])
multi_2 = MultiPolygon([poly2_2, poly3_2])

areas = {
    "kde": [75, 95, 75, 95],
    "geometry": [poly1, multi, poly1_2, multi_2],
    "Variable": ["variable1", "variable1", "variable2", "variable2"],
}

gdf = gpd.GeoDataFrame(areas, crs="EPSG:2056")
gdf["area"] = gdf["geometry"].area / 10**6

plot_kde(data=gdf)