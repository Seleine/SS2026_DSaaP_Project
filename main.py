########################################
# Libraries
########################################
import customised_variables
import home_coords
from read_gps_data import read_gps_data
from calculate_phases_of_the_day import calculate_phases_of_the_day
from remove_home_points import remove_home_points
from static_not_static import create_static_column, sample_plot_static_not_static

########################################
# Read in Meteo Data
########################################


########################################
# Determine buffer around home coordinates
########################################
home_buffer = home_coords.home_coords.buffer(customised_variables.buffer_around_home)

########################################
# Read in GPS data
########################################

data = read_gps_data(
    file_path = customised_variables.file_path,
    gpx_layer = customised_variables.gpx_layer,
    time_zone = customised_variables.time_zone
)

########################################
# Phases of the Day
########################################

data = calculate_phases_of_the_day(data = data)

########################################
# Remove Home Coordinates
########################################

data = remove_home_points(data = data, home_buffer = home_buffer)

del home_buffer

########################################
# Calculate Time Lag and Check Speed Value
########################################


########################################
# Summary Table
########################################


########################################
# Calculate Time Lag and Check Speed Value 2
########################################$


########################################
# Summary Table 2
########################################


########################################
# KDE Plot Phases of the Day
########################################


########################################
# Join GPS and Meteo Data
########################################


########################################
# Precipitation
########################################


########################################
# KDE Plot Precipitation
########################################


########################################
# Movement Analysis
########################################

data = create_static_column(data = data, buffer = customised_variables.buffer_intersection)

sample_plot_static_not_static(data = data, start_date = "2024-04-01 00:00:00", end_date = "2024-04-01 18:00:00")

########################################
# KDE Plot Movement Analysis
########################################