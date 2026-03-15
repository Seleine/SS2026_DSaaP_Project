library(dplyr)
library(sf)

# function calculating difference between two data points by second
calculate_timediff_seconds <- function(later, now){
  as.numeric(difftime(later, now, units = "secs"))
}

# functions for calculating distance by element and time difference.
calculate_distance_by_element <- function(later, now) {
  as.numeric(
    st_distance(later, now, by_element = TRUE)
  )
}

# function for calculating timelag  
calculate_timelag_steplength <- function(data, datetime, geometry) {
  data <- data |>
    arrange(datetime) |> # make sure order is correct
    mutate(timelag = calculate_timediff_seconds(later=lead(datetime), now=datetime),
           steplength = calculate_distance_by_element(later=lead(geometry), now=geometry)
    )
  return(data)
}

# function for calculating speed 
calculate_speed <- function(data, datetime) {
  data <- data |>
    arrange(datetime) |> # make sure order is correct
    mutate(speed_ms = (steplength/timelag), #Calculate speed in m/s  
           speed_kmh = (steplength/timelag)*3.6 # Calculate speed in km/h
    )
  return(data)
}
