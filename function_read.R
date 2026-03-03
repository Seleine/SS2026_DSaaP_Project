function_read <- function(path) {
  
  data <- st_read(path, layer = "layer")
  
  data$month <- factor(data$month,
                       levels = c("April", "May", "June", "July","August",
                                  "September", "October", "November",
                                  ordered = TRUE))
  return(data)
}