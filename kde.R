library(smoothr)
library(adehabitatHR)
library(sf)
library(leaflet)
library(leaflet.extras)

calculate_kde_from_gps_points <- function(data) {
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

plot_kde <- function(data, palette_of_choice) {
  # change to 4326 for leaflet
  data_wgs <- st_make_valid(st_transform(data, 4326))
  
  # colour palette in relation to area per phase
  pal <- colorNumeric(palette = palette_of_choice, domain = data_wgs$area)
  
  # initialise leaflet map
  leaflet_map <- leaflet() |>
    addProviderTiles(providers$Esri.WorldImagery, group = "World Imagery") |> 
    addResetMapButton() # add home button
  
  # split sf object by day phase
  variables <- split(data_wgs, data_wgs$Variable)
  
  # add one group per phase
  for (variable_name in names(variables)) { # "Dawn"  "Day"   "Dusk"  "Night"
    leaflet_map <- leaflet_map |> 
      addPolygons(
        data = variables[[variable_name]], # the different areas (UD) per day phase
        fillColor = ~pal(area),
        fillOpacity = 0.4,
        color = "darkgrey", # line
        weight = 1, # line
        group = variable_name, 
        label = ~paste0("Area: ", round(area, 2)), # while hovering over areas in map
        highlightOptions = highlightOptions(color = "white", weight = 2, bringToFront = FALSE)
      )
  }
  
  # radio buttons for home ranges per day phase
  leaflet_map <- leaflet_map |> 
    addLayersControl(
      baseGroups = names(variables),
      options = layersControlOptions(collapsed = FALSE)
    )
  
  return(leaflet_map)
}