import seaborn as sns
import geopandas as gpd
import os
import webbrowser
import matplotlib.pyplot as plt


def barplot_counts(data: gpd.GeoDataFrame, x_variable: str, title: str, plot_name: str):
    """
    Creates and saves a count bar plot for a given variable in a GeoDataFrame,
    then opens it in the default web browser.

    Parameters
    ----------
    data: gpd.GeoDataFrame
        The input GeoDataFrame containing the data to plot.
    x_variable: str
        The column name in `data` to count and display on the x-axis.
    title: str
        The title to display on the plot.
    plot_name: string of plot name

    Raises
    ------
    ValueError
        If `x_variable` is not a column in `data`.
    TypeError
        If `data` is not a GeoDataFrame.
    """
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError(f"Expected a GeoDataFrame, got {type(data).__name__}.")
    if x_variable not in data.columns:
        raise ValueError(f"Column '{x_variable}' not found in GeoDataFrame.")
    if not title or not isinstance(title, str):
        raise ValueError("Title must be a non-empty string.")

    ax = sns.countplot(data, x=x_variable)
    ax.set_title(title)

    if not os.path.exists("./plots"):
        os.mkdir("./plots")

    output_path = os.path.abspath(f"./plots/barplot_count_data_points_{plot_name}.png")
    ax.get_figure().savefig(output_path, bbox_inches="tight")
    plt.close()

    webbrowser.open(f"file://{output_path}")
