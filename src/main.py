########################################
# Libraries
########################################
import config
import geopandas as gpd
import home_coords
from read_gps_data import read_gps_data
from calculate_phases_of_the_day import calculate_phases_of_the_day
from remove_home_points import remove_home_points
from static_not_static import create_static_column
from static_not_static_plot import sample_plot_static_not_static
from speed import calculate_timelag_steplength_speed
from summary_table import summary_table
from kde import calculate_kde_from_gps_points
from kde_plot import plot_kde
from bar_plot_counts import barplot_counts
from pathlib import Path


def main():
    ########################################
    # Determine buffer around home coordinates
    ########################################

    home_buffer = home_coords.home_coords.buffer(config.buffer_around_home)

    ########################################
    # Read in GPS data
    ########################################

    data_path = config.file_path

    data = read_gps_data(
        file_path=Path(__file__).resolve().parent.parent / data_path,
        gpx_layer=config.gpx_layer,
        time_zone=config.time_zone,
    )

    ########################################
    # Phases of the Day
    ########################################

    data = calculate_phases_of_the_day(data=data)

    ########################################
    # Remove Home Coordinates
    ########################################

    data = remove_home_points(data=data, home_buffer=home_buffer)

    del home_buffer

    ########################################
    # Calculate Time Lag and Check Speed Value
    ########################################

    data = calculate_timelag_steplength_speed(
        data=data, datetime_col="time", geometry_col="geometry"
    )

    # all rows containing a speed value > 48 km/h will be removed
    data = data[data["speed_kmh"] < 48]

    ########################################
    # Summary Table
    ########################################

    summary_table(
        data=data,
        datetime_col="time",
        table_name="summary_table_before_outlier_deletion",
    )

    ########################################
    # Calculate Time Lag and Check Speed Value 2
    ########################################

    # Data points with a time lag < 9 minutes will be removed. This faciliates the calculation of static and non-static phases.
    data = data[data["timelag"] >= 540]

    # generate new unique id
    data["track_seg_point_id"] = range(1, len(data) + 1)

    # Now the speed value and the time lag has to be recalculated.
    data = calculate_timelag_steplength_speed(
        data=data, datetime_col="time", geometry_col="geometry"
    )

    ########################################
    # Summary Table 2
    ########################################

    summary_table(
        data=data,
        datetime_col="time",
        table_name="summary_table_after_outlier_deletion",
    )

    ########################################
    # KDE Plot Phases of the Day
    ########################################

    barplot_counts(
        data=data,
        x_variable="dayphase",
        title="Number of Data Points per Day Phase",
        plot_name="dayphases",
    )

    kde_night = calculate_kde_from_gps_points(
        data=data[data["dayphase"] == "Nighttime"], variable_name="Nighttime"
    )
    kde_day = calculate_kde_from_gps_points(
        data=data[data["dayphase"] == "Daytime"], variable_name="Daytime"
    )
    kde_dusk = calculate_kde_from_gps_points(
        data=data[data["dayphase"] == "Dusk"], variable_name="Dusk"
    )
    kde_dawn = calculate_kde_from_gps_points(
        data=data[data["dayphase"] == "Dawn"], variable_name="Dawn"
    )

    kde_dayphases = gpd.pd.concat([kde_night, kde_day, kde_dusk, kde_dawn])
    kde_dayphases = gpd.GeoDataFrame(kde_dayphases)

    plot_kde(data=kde_dayphases, plot_name="kde_dayphases")

    ########################################
    # Movement Analysis
    ########################################

    data = create_static_column(data=data, buffer=config.buffer_intersection)

    sample_plot_static_not_static(
        data=data, start_date="2024-04-01 00:00:00", end_date="2024-04-01 18:00:00"
    )

    ########################################
    # KDE Plot Movement Analysis
    ########################################

    barplot_counts(
        data=data,
        x_variable="static",
        title="Number of Data Points per Movement Phase",
        plot_name="movement",
    )

    kde_static = calculate_kde_from_gps_points(
        data=data[data["static"] == "Static"], variable_name="Static"
    )
    kde_not_static = calculate_kde_from_gps_points(
        data=data[data["static"] == "Not Static"], variable_name="Not Static"
    )

    kde_movement = gpd.pd.concat([kde_static, kde_not_static])

    plot_kde(data=kde_movement, plot_name="kde_movement")


if __name__ == "__main__":
    main()
