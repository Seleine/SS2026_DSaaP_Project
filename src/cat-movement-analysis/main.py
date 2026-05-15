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
from generate_report import generate_report


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

    # all rows containing a speed value > value in config file km/h will be removed
    data = data[data["speed_kmh"] < config.max_speed_kmh]

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

    # Data points with a time lag < value in config file minutes will be removed. This facilitates the calculation of static and non-static phases.
    data = data[data["timelag"] >= config.min_timelag_s]

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

    STRUCTURE = [
        {
            "title": "Quality Control",
            "level": 2,
            "content": [],
            "text": "This section summarises the quality control steps applied to the raw GPS data.",
            "subsections": [
                {
                    "title": "Summary Table",
                    "level": 3,
                    "text": "The first table gives an overview of the data points before outlier deletion. Outliers are data points which result in a speed value larger than the set value in the config file. Furthermore, data points which have a time lag smaller than the specified value in the config file are deleted, which increases data quality. Therefore, in the second table there should be no data points with a time lag smaller than the set value.",
                    "content": [
                        "quality_control/summary_table_before_outlier_deletion.html",
                        "quality_control/summary_table_after_outlier_deletion.html",
                    ],
                },
                {
                    "title": "Number of Data Points",
                    "level": 3,
                    "text": "These two plots show the number of data points after outlier deletion, either separated by day or movement phase.",
                    "content": [
                        "quality_control/barplot_count_data_points_dayphases.png",
                        "quality_control/barplot_count_data_points_movement.png",
                    ],
                },
                {
                    "title": "Sample Plot for Movement Phases",
                    "level": 3,
                    "text": "This interactive map shows the idea behind the separation of moving and static phases. Is a point within the set buffer of the previous or following point, it is determined as static.",
                    "content": [
                        "plots/sample_plot_static.html",
                    ],
                },
            ],
        },
        {
            "title": "Products",
            "level": 2,
            "text": "The interactive maps show the KDE for the different phases.",
            "content": [
                "plots/kde_dayphases.html",
                "plots/kde_movement.html",
            ],
        },
    ]

    generate_report(
        structure=STRUCTURE,
        output_path="report.html",
        base_dir="..",
        report_title="Report",
    )
