import seaborn as sns
import geopandas as gpd
import os
import matplotlib.pyplot as plt


def barplot_counts(
    data: gpd.GeoDataFrame, x_variable: str, title: str, plot_name: str
) -> None:
    """
    Creates and saves a count bar plot for a given variable in a GeoDataFrame.

    Parameters
    ----------
    data : gpd.GeoDataFrame
        The input GeoDataFrame containing the data to plot.
    x_variable : str
        The column name in `data` to count and display on the x-axis.
    title : str
        The title to display on the plot.
    plot_name : str
        The name of the saved plot file.

    Returns
    -------
    None
        Saves the png to the working directory.

    Raises
    ------
    TypeError
        If ``data`` is not a GeoDataFrame.
    ValueError
        If ``x_variable`` is not a column in ``data``.
    """
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError(f"Expected a GeoDataFrame, got {type(data).__name__}.")
    if not isinstance(x_variable, str):
        raise TypeError(
            f"Expected x_variable to be a str, got {type(x_variable).__name__}."
        )
    if not isinstance(title, str):
        raise TypeError(f"Expected title to be a str, got {type(title).__name__}.")
    if not isinstance(plot_name, str):
        raise TypeError(
            f"Expected plot_name to be a str, got {type(plot_name).__name__}."
        )
    if x_variable not in data.columns:
        raise ValueError(f"Column '{x_variable}' not found in GeoDataFrame.")

    ax = sns.countplot(data, x=x_variable)
    ax.set_title(title)

    if not os.path.exists("./quality_control"):
        os.mkdir("./quality_control")

    output_path = os.path.abspath(
        f"./quality_control/barplot_count_data_points_{plot_name}.png"
    )
    ax.get_figure().savefig(output_path, bbox_inches="tight")
    plt.close()
