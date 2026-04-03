import geopandas as gpd

def read_months_ordered_gpkg(path, layer):
    data <- gdp.read_file(path, layer=layer)

    months_categories = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                         "October", "November", "December"]

    data["month"] = gpd.Categorical(data["month"], categories=months_categories)
    data.sort_values(by="month")

    return data