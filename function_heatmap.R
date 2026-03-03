# https://ggplot2.tidyverse.org/reference/geom_density_2d.html
# https://github.com/nsgrantham/ggdark

library(ggmap)
library(osmdata)
library(ggspatial)

fct_heatmap <- function(data, title){
  bbox <- c(8.558, 47.358, 8.565, 47.360)
  
  osm <- opq(bbox = bbox) |> 
    add_osm_feature(key = "highway") |> 
    osmdata_sf()
  
  heatmap_plot <- ggplot() +
    geom_sf(data = osm$osm_lines, color = "grey") +
    
    # Contour lines
    geom_density2d(data = data, aes(x = lon, y = lat), 
                   linewidth = 0.5, color = "black") +
    
    # KDE heatmap with manually scaled level
    stat_density2d(
      data = data,
      aes(
        x = lon, y = lat,
        fill = after_stat(level / max(level, na.rm = TRUE)),  # manual normalisation (0, 1)
        alpha = after_stat(level / max(level, na.rm = TRUE)) # the higher the value, the less transparent
      ),
      geom = "polygon", bins = 20
    ) +
    
    # colourisation with gradient (from red to blue)
    scale_fill_gradient(
      low = "blue", high = "red",
      name = "Density"
    ) +
    
    # remove alpha legend (transparency)
    scale_alpha(guide = "none") +
    
    # geom_hline(yintercept= 47.360, colour="red") + # home 1
    # geom_vline(xintercept=8.564, colour="red") +
    # 
    # geom_hline(yintercept= 47.36001, colour="yellow") + # home 2
    # geom_vline(xintercept=8.56364, colour="yellow") +
    
    # Labels and theme
    labs(x = "Longitude", y = "Latitude", title = title) +
    coord_sf() +
    dark_theme_dark() +
    theme(
      axis.title = element_blank(),
      plot.background = element_rect(fill = "grey10", colour = "grey10")
    )
  
  return(heatmap_plot)
}