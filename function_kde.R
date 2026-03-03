library(smoothr)
library(adehabitatHR)

function_kde <- function(data) {
  # input: a spatial data frame
  # This data contains point locations
  
  st_geometry(data) <- "geometry"
  # ensures that the geometry column in the data frame is recognised as the spatial geometry by the sf package.
  
  sp_points <- as(data, "Spatial")
  # converts the sf object data to a SpatialPointsDataFrame (from the sp package),
  # because the `kernelUD()` function from the adehabitatHR package requires
  # spatial objects in this format.
  
  kud <- kernelUD(sp_points)
  # probabilistic estimate of space use based on the input point locations
  # each cell in the surface represents the estimated probability that the animal is present there.
  
  range95 <- smooth(st_as_sf(getverticeshr(kud, percent = 95)))
  range75 <- smooth(st_as_sf(getverticeshr(kud, percent = 75)))
  range50 <- smooth(st_as_sf(getverticeshr(kud, percent = 50)))
  range25 <- smooth(st_as_sf(getverticeshr(kud, percent = 25)))
  range10 <- smooth(st_as_sf(getverticeshr(kud, percent = 10)))
  # compute homeranges for 95%, 75%, 50%, 25%, 10% of points, objects are returned as spatial polygon data frames
  # getverticeshr: extracts the home range contour (a polygon) that encompasses that percent of the probability distribution.
  # st_as_sf(): converts the resulting SpatialPolygonsDataFrame back into an sf object.
  
  ranges <- rbind(range95, range75, range50, range25, range10)
  
  return(ranges)
}