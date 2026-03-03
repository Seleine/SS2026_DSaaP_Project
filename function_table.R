# function to generate a summary table
function_table <- function(data) {
  data_no_geo <- data |>
    st_drop_geometry() |> 
    group_by(month) |> 
    arrange(time) |>
    rename("Month" = month) |> 
    mutate(timestamp = difftime_secs(lead(time), time),
           timestamp_min = as.integer(difftime_secs(lead(time), time)/60))
  
  table <- summarise(data_no_geo,
                     "Median Interval (min)"= round(median(timestamp, na.rm = TRUE)/60, digits=2),
                     "Mean Interval (min)"= round(mean(timestamp, na.rm = TRUE)/60, digits=2),
                     "Min Interval (s)" = min(timestamp, na.rm=TRUE),
                     "Max Interval (h)" = round(max(timestamp, na.rm=TRUE)/3600, digits=2),
                     "Count (points)" = n(),
                     "Count < 9  min" = sum(timestamp < 540, na.rm = TRUE),
                     "Proportion (%)" =  round(sum(timestamp < 540, na.rm = TRUE) / n(), digits = 2)*100,
                     .groups = "drop")
  
  return(table)
}