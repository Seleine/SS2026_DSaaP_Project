library(dplyr)
library(sf)

# function calculating difference between two data points by second
difftime_secs <- function(later, now){
  as.numeric(difftime(later, now, units = "secs"))
}

# functions for calculating distance by element and time difference.
distance_by_element <- function(later, now) {
  as.numeric(
    st_distance(later, now, by_element = TRUE)
  )
}

# function for calculating speed  
function_speed <- function(data, datetime, geometry) {
  data <- data |>
    arrange(datetime) |> # make sure order is correct
    mutate(steplength = distance_by_element(later=lead(geometry), now=geometry),
           speed_ms = round((steplength / timelag), digits = 2),   # calulate m/s
           speed_kmh = round((steplength / timelag) * 3.6, digits = 2)   # calulate km/h
    )
  return(data)
}
