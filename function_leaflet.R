library(sf)
library(leaflet)
library(leaflet.extras)

fct_leaflet <- function(data, palette_of_choice) {
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